"""Sublab Medium - one Kazakh-correction task, six models.

Six models, one prompt, eight sentences. What you are producing is evidence:
a table that says which models repaired which kind of damage, and what each one
charged you for the attempt.

Fill in every `TODO`. Keep the function signatures.
"""

import json
import sys
from pathlib import Path
import re

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sublab_easy.registration_bot import (RATES_PER_MTOK,  # noqa: E402
                                          ask_once, estimate_cost)

DATA = Path(__file__).resolve().parent.parent / "data" / "kazakh_errors.json"

# Every model you must run. Keep the order - it is the order of your table.
MODELS = [
    ("openai", "gpt-5.6-luna"),
    ("openai", "gpt-5.6-terra"),
    ("openai", "gpt-5.6-sol"),
    ("openrouter", "nemotron-3-ultra-550b-a55b:free"),
    ("openrouter", "nex-n2.5-mini:free"),
    ("openrouter", "laguna-s-2.1:free"),
]


def load_sentences() -> list[dict]:
    """The eight corrupted sentences and their published originals."""
    return json.loads(DATA.read_text(encoding="utf-8"))["sentences"]


def build_prompt(corrupted: str) -> str:
    """Ask for a corrected sentence AND a list of the changes made."""
    return (
        "The following text is Kazakh, taken from a real published news "
        "sentence, but it has been corrupted. Possible damage includes: "
        "Kazakh-specific letters (ә, қ, ң, ғ, ү, ұ, і, ө, һ) replaced with "
        "similar-looking Russian/Cyrillic letters; Cyrillic letters replaced "
        "with similar-looking Latin letters (homoglyphs); a hyphen removed; "
        "two words joined together with no space; or a letter doubled.\n\n"
        "Fix the text so it reads as correct, natural Kazakh.\n\n"
        f"Corrupted text:\n{corrupted}\n\n"
        "Respond with exactly this JSON object and nothing else - no "
        "markdown fences, no explanation before or after it:\n"
        '{"corrected": "...", "changes": ["...", "..."]}\n\n'
        '"corrected" is the fixed Kazakh sentence. "changes" is a short '
        "list of the specific edits you made (e.g. \"ә restored to а in "
        "'мемлекеттін'\")."
    )


def parse_response(text: str) -> dict:
    """Pull {"corrected": str, "changes": list} out of the model's reply.

    Models wrap JSON in prose, or in ```json fences, more often than you would
    like. Be forgiving: find the JSON, parse it, and raise ValueError with the
    offending text if you truly cannot.
    """
    # 1. Try the whole string as-is.
    try:
        data = json.loads(text)
        if isinstance(data, dict) and "corrected" in data:
            return data
    except (json.JSONDecodeError, TypeError):
        pass
 
    # 2. Look for a ```json ... ``` or ``` ... ``` fenced block.
    fence_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if fence_match:
        try:
            data = json.loads(fence_match.group(1))
            if isinstance(data, dict) and "corrected" in data:
                return data
        except json.JSONDecodeError:
            pass
 
    # 3. Scan for balanced {...} objects anywhere in the text and try each
    #    one (a model may chat before/after the JSON).
    decoder = json.JSONDecoder()
    for i, ch in enumerate(text):
        if ch != "{":
            continue
        try:
            data, _ = decoder.raw_decode(text, i)
        except json.JSONDecodeError:
            continue
        if isinstance(data, dict) and "corrected" in data:
            return data
 
    raise ValueError(f"No parsable JSON with a 'corrected' field found in: {text!r}")


def correct_with(model: str, corrupted: str, via: str) -> dict:
    """Send one sentence to one model.

    Returns:
        {"corrected": str, "changes": list, "input_tokens": int,
         "output_tokens": int, "model": str}

    `via` is "openai" or "openrouter" and goes straight through to
    `ask_once` from sublab_easy - there is no conversation here, just one
    prompt and one reply, eight times per model.
    """
    prompt = build_prompt(corrupted)
    response = ask_once(prompt, model=model, via=via)
 
    parsed = parse_response(response["text"])
 
    return {
        "corrected": parsed.get("corrected", ""),
        "changes": parsed.get("changes", []),
        "input_tokens": response["input_tokens"],
        "output_tokens": response["output_tokens"],
        "model": model,
    }


def score_correction(returned: str, expected: str) -> dict:
    """Compare a model's output against the published original.
 
    `exact` is a signal, not a grade: good Kazakh that differs from the
    original (different word order, synonym, alternate valid suffix) still
    counts as a real correction - say so in the written analysis, don't just
    report the number below as "accuracy".
    """
    exact = returned == expected
 
    min_len = min(len(returned), len(expected))
    positional_diff = sum(
        1 for a, b in zip(returned[:min_len], expected[:min_len]) if a != b
    )
    length_diff = abs(len(returned) - len(expected))
    char_diff = positional_diff + length_diff
 
    return {"exact": exact, "char_diff": char_diff}


def run_all() -> list[dict]:
    """Every model against every sentence. One row per (model, sentence)."""
    rows = []
    for via, model in MODELS:
        for s in load_sentences():
            print(f"  {via}/{model} -> {s['id']} ...", end=" ", flush=True)
            try:
                r = correct_with(model, s["corrupted"], via)
            except Exception as exc:            # a model failing IS a result
                print("FAILED:", repr(exc))
                rows.append({"model": model, "id": s["id"],
                             "errors": s["errors"], "failed": repr(exc)})
                continue
            print("ok")
            rate_in, rate_out = RATES_PER_MTOK[model]
            rows.append({
                "model": model,
                "id": s["id"],
                "errors": s["errors"],
                "corrected": r["corrected"],
                "changes": r["changes"],
                **score_correction(r["corrected"], s["correct"]),
                "cost": estimate_cost(r["input_tokens"], r["output_tokens"],
                                      rate_in, rate_out),
                "input_tokens": r["input_tokens"],
                "output_tokens": r["output_tokens"],
            })
    return rows


def summarise(rows: list[dict]) -> None:
    """Per-model totals, to paste into SUBMISSION.md."""
    print(f"{'model':38}{'exact':>7}{'failed':>8}{'tokens':>9}{'cost $':>10}")
    print("-" * 72)
    for _, model in MODELS:
        mine = [r for r in rows if r["model"] == model]
        exact = sum(1 for r in mine if r.get("exact"))
        failed = sum(1 for r in mine if r.get("failed"))
        toks = sum(r.get("input_tokens", 0) + r.get("output_tokens", 0) for r in mine)
        cost = sum(r.get("cost", 0.0) for r in mine)
        print(f"{model:38}{exact:>7}{failed:>8}{toks:>9}{cost:>10.5f}")


if __name__ == "__main__":
    out = run_all()
    summarise(out)
    dest = Path(__file__).resolve().parent.parent / "outputs"
    dest.mkdir(exist_ok=True)
    (dest / "corrections.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nwrote outputs/corrections.json ({len(out)} rows)")
