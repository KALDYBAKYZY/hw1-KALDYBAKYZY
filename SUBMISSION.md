# HW1 submission

**Name: Zhaiylgan Gulnaz**
**Student ID: s23067637**
**Group: CSS4007-ENG-10**
**Repository: hw1-KALDYBAKYZY**

## AI tool disclosure

> I used Claude (an AI tool from Anthropic) for four things:
> 1. To understand the tasks in the homework.
> 2. To write the code: `sublab_easy/registration_bot.py`, `sublab_medium/correct_kazakh.py`, and `sublab_hard/tokenizer_forensics.py`. My Python level is not enough to write all of this myself.
> 3. In Sublab Harder, to understand what a tokenizer is and how it works.
> 4. To check this submission.md file, and to check the numbers in it.
>
> I wrote the prompts sent to the models, and I wrote all the text parts of this submission myself (the written answers, the explanations, the "changes" analysis).

---

## Sublab Easy — the registration bot and its bill

**How I laid the catalogue out inside the system prompt, and why:**

> Four parts, in this order:
> 1. A strict rule: use ONLY the information in the prompt. Never invent a course. If a course is not in the catalogue, say it does not exist.
> 2. The rules: minimum 15 credits, maximum 30 credits, and a note about time collisions.
> 3. The student: ID, year, programme, completed courses.
> 4. The catalogue: one line per course, same fields with "|": code, title, credits, prerequisites, schedule, seats remaining, instructor.
>
> Why:
> - The rule is first, so the bot reads "do not invent anything" before the data.
> - One line per course with the same fields is easy to search and compare.
> - I counted the seats in the code and wrote "2/40", so the model does not need to subtract.
> - The schedule is simple text (Tuesday 09:00-10:50), so time collisions are easy to see.

**My turn 5 (Kazakh or Russian):**

> Я студент третьего курса. На какие курсы я всё ещё могу записаться?
> (It is the same question as turn 1, but in Russian.)

### Run 1 — OpenAI, `gpt-5.6-luna`

| Turn | Input tokens | Output tokens | Cost $ |
|---|---|---|---|
| 1 | 657 | 520 | 0.000755 |
| 2 | 903 | 197 | 0.000417 |
| 3 | 1008 | 98 | 0.000319 |
| 4 | 1085 | 27 | 0.000249 |
| 5 | 1136 | 355 | 0.000653 |
| **total** | 4789 | 1197 | 0.002394 |

### Run 2 — OpenRouter, `deepseek/deepseek-v4-flash-0731:free`

| Turn | Input tokens | Output tokens | Cost $ |
|---|---|---|---|
| 1 | 734 | 1761 | 0.000000 |
| 2 | 1227 | 275 | 0.000000 |
| 3 | 1414 | 314 | 0.000000 |
| 4 | 1557 | 271 | 0.000000 |
| 5 | 1660 | 2006 | 0.000000 |
| **total** | 6592 | 4627 | 0.000000 |

### Turn 4, verbatim

**OpenAI:**

```
I can’t add **CSS-4090 Quantum Machine Learning** because it does not exist in the provided course catalogue.
```

**OpenRouter:**

```
 **CSS-4090 "Quantum Machine Learning" does not exist in the course catalogue.**
 
I cannot register you for a course that is not listed. Please double-check the course code and title, or ask about any of the courses currently in the catalogue (for example, CSS-4007, CSS-4102, CSS-4400, etc.) if you meant one of those.
```

### Written answers

**1. The two providers used almost identical code. What actually changed, and what did not?**

> What changed:
> - the base_url (OpenRouter: https://openrouter.ai/api/v1);
> - the API key (OPENROUTER_API_KEY instead of OPENAI_API_KEY);
> - the model name;
> - the model line in the price table (RATES_PER_MTOK). The free model costs 0.
>
> What did not change:
> - the same OpenAI class from the same library;
> - the same call, client.chat.completions.create(...);
> - the same message format (system, user, assistant);
> - the same usage fields (prompt_tokens, completion_tokens);
> - the same run_turn function and the same system prompt.
>
> One thing I noticed: the first message was 657 tokens for OpenAI and 734 for DeepSeek, with exactly the same text. Each model has its own tokenizer.

**2. Why did the input token count climb on every turn? What happens to the bill at fifty turns?**

> The model remembers nothing between calls. On every turn my code sends the whole conversation again: the system prompt, all old questions, all old answers, and the new question.
>
> OpenAI input: 657 → 903 → 1008 → 1085 → 1136. DeepSeek: 734 → 1227 → 1414 → 1557 → 1660. In turn 1, about 640 of the 657 tokens are the system prompt. Example: turn 4 had 27 output tokens, and my new Russian question is about 24 tokens. 27 + 24 = 51, and the input grew by 51 from turn 4 to turn 5. It matches. In other turns the output is bigger than the growth (turn 1: 520 output, +246). I think this is because hidden reasoning tokens are not sent back.
>
> At fifty turns (estimate): the input grows about 120 tokens per turn (657 → 1136 in 4 steps).
> - Turn 50 input: about 657 + 49 × 120 ≈ 6,500 tokens.
> - Total input over 50 turns: about 180,000 tokens. Without history it would be about 33,000, so it is 5.5 times more.
> - The history part grows like n × n: twice the turns, about four times the history.
> - Cost of 180,000 input tokens: about $0.04 on gpt-5.6-luna ($0.20 per million), but about $0.90 on gpt-5.6-sol ($5 per million).

**3. Turn 4: did the bot refuse, or did it invent CSS-4090?**

> Both bots refused. They said the course is not in the catalogue. They did not invent credits, a room or an instructor. DeepSeek also asked me to check the course code.
>
> What held the line: the rule at the top of my system prompt. It says to use ONLY the information below, and "If the student asks about a course that is not in this catalogue, refuse and say plainly that it does not exist in the catalogue". The bot also had the full list of real courses to compare with.
>
> The tables above are from my first run. I ran the script once more, and both bots refused again (2 out of 2 runs for each model). In the second run, DeepSeek did not repeat the CSS-4090 request, but the same behaviour held on the other turns (see point 4).

**4. Where else was either bot wrong?**

> Same-hour courses: both bots noticed. CSS-4007 and CSS-4102 both meet on Tuesday 09:00-10:50. Both bots warned in turn 1, and in turn 2 both refused to register the two together.
>
> Full courses: both bots noticed. CSS-4400 (25 of 25) and CSS-3011 (60 of 60) are full. Both said CSS-4400 is full and did not offer it. Courses with few seats, CSS-4007 (2 left) and FIN-3300 (1 left), were correctly shown as open.
>
> Where the bots were wrong:
> - OpenAI, turn 2 (run 1): it said "choose one and add eligible courses to reach at least 15 credits". This is not possible. The open courses are CSS-4007 (6 credits), CSS-4102 (5) and FIN-3300 (5), and the two CSS courses collide. The best total is CSS-4007 + FIN-3300 = 11 credits, less than 15. The advice is wrong.
> - DeepSeek, turns 1 and 5 (run 1): it talked about "course overload exception", "waitlist/override" and an academic advisor. None of this is in my catalogue or rules. It made up a policy.
> - DeepSeek writes too much: 1761 and 2006 output tokens in turns 1 and 5 (run 1).
> - Not every time: in my second run OpenAI did not give the 15-credit advice again, and DeepSeek did not mention overload, waitlist or override again — but in both runs it still pointed me to an advisor or administrator when 15 credits could not be reached.

---

## Sublab Medium — one task, six models

| Model | Exact | Failed | Tokens | Cost $ |
|---|---|---|---|---|
| nex-n2.5-mini:free | 7 | 0 | 10670 | 0.00000 |
| laguna-s-2.1:free | 2 | 0 | 9551 | 0.00000 |
| nemotron-3-ultra-550b-a55b:free | 2 | 0 | 61102 | 0.00000 |
| gpt-5.6-luna | 7 | 0 | 4540 | 0.00373 |
| gpt-5.6-terra | 7 | 0 | 3408 | 0.02374 |
| gpt-5.6-sol | 8 | 0 | 3269 | 0.05517 |

### Which error types did each model repair?

| Error type | nex | nemotron | laguna | luna | terra | sol |
|---|---|---|---|---|---|---|
| kaz_to_rus | partial | partial | no | yes | yes | yes |
| latin_homoglyph | yes | partial | yes | yes | yes | yes |
| drop_hyphen | yes | no | no | yes | yes | yes |
| join_words | yes | partial | partial | yes | yes | yes |
| double_letter | yes | partial | partial | yes | yes | yes |

("partial" = fixed in some sentences but not all, or fixed the error but also changed other words.)

**The `latin_homoglyph` row: what happened?**

> On both homoglyph sentences (KZ-03 and KZ-08), five models gave the exact right sentence: luna, terra, sol, nex and laguna. Only nemotron did not.
>
> On KZ-03, nemotron did not restore the original word letter by letter. It replaced "Алаяқтарға" with "Алдаушыларға" — a real Kazakh word, close in meaning (also roughly "to scammers"), but a different word, not a letter fix (char_diff 51).
>
> On KZ-08, nemotron did restore the homoglyph letters correctly (Latin o, a, T → Cyrillic о, а, Т), but it also added the word "мен" and changed "кездескісі" to "кездесуі". So the row is scored partial: one sentence replaced with a synonym instead of a letter fix, one fixed at the letter level but with extra changes.
>
> Laguna gave the right sentences for both, but its list of changes made no sense (for example, "ә restored from а" repeated for almost every word, even ones that have no ә). I do not trust its explanations, only its final output.

**Where a model returned good Kazakh that was not identical to the original:**

> - `gpt-5.6-luna`, KZ-04: it added a "?" at the end. The letter fixes (жалған, үшін) are correct.
> - `gpt-5.6-terra`, KZ-05: it split the joined words correctly and only added a "?".
> - `nemotron`, KZ-03: the opposite case — a real, meaningful Kazakh word ("Алдаушыларға"), but not the original one, so it still counts as wrong for this task. Exact match is not correctness, but correctness is not "any real word" either.

**Cheapest model that was good enough, and why:**

> `gpt-5.6-luna`. It has 7/8 exact. The 8th (KZ-04) is also correct, with only an extra "?", so it is really 8/8. It cost $0.00373, about 15 times cheaper than `gpt-5.6-sol` ($0.05517), with almost the same quality.
>
> The free model `nex-n2.5-mini` also has 7/8 and costs $0. But its miss (KZ-01) is a real mistake: it did not fix "Касым" and "Токаев", and it changed "елшісінен" to "елшілерінен" (wrong plural form, a different word). It also used more tokens than luna (10,670 against 4,540). So luna is safer. If a small mistake is OK, nex is the cheapest. `nemotron` and `laguna` (2/8 exact, with real word mistakes) are too weak for this task.

---

## Sublab Harder — open the tokenizer

## A. What a language costs

"× English" = tokens per character compared with English. Money = 1,000 sentences, input price $5.00 per million tokens.

**cl100k_base:**

| Language | Tokens | Chars | Tok/char | × English | $ per 1,000 sentences |
|---|---|---|---|---|---|
| kk | 200 | 263 | 0.760 | 3.75 | $0.1667 |
| ru | 129 | 277 | 0.466 | 2.30 | $0.1075 |
| en | 59 | 291 | 0.203 | 1.00 | $0.0492 |

**o200k_base:**

| Language | Tokens | Chars | Tok/char | × English | $ per 1,000 sentences |
|---|---|---|---|---|---|
| kk | 84 | 263 | 0.319 | 1.58 | $0.0700 |
| ru | 74 | 277 | 0.267 | 1.32 | $0.0617 |
| en | 59 | 291 | 0.203 | 1.00 | $0.0492 |

## B. What a homoglyph does

Tokenizer: o200k_base. KZ-08 also has a double letter.

| Sentence id | Foreign char (index, name) | Tokens correct | Tokens corrupted | Δ | Diverges at |
|---|---|---|---|---|---|
| KZ-03 | (0, LATIN CAPITAL LETTER A), (2, LATIN SMALL LETTER A), (5, LATIN SMALL LETTER T) | 16 | 20 | +4 | 0 |
| KZ-08 | (1, LATIN SMALL LETTER O), (3, LATIN SMALL LETTER A), (9, LATIN CAPITAL LETTER T) | 21 | 24 | +3 | 1 |

Token pieces around the divergence:

**KZ-03**

```
correct  : ['А', 'лая', 'қ', 'тарға', ' ақша', 'ңызды', ' ауд', 'арып', ' қой', 'са', 'ңыз', ' не', ' і', 'сте', 'у', ' керек']
corrupted: ['A', 'л', 'a', 'я', 'қ', 't', 'ар', 'ға', ' ақша', 'ңызды', ' ауд', 'арып', ' қой', 'са', 'ңыз', ' не', ' і', 'сте', 'у', ' керек']
```

**KZ-08**

```
correct  : ['Д', 'он', 'аль', 'д', ' Т', 'рамп', ' К', 'им', ' Ч', 'ен', ' Ы', 'н', 'мен', ' осы', ' күз', 'де', ' қайта', ' кездес', 'кі', 'сі', ' келеді']
corrupted: ['Д', 'o', 'н', 'a', 'л', 'ль', 'д', ' T', 'рамп', ' К', 'им', ' Ч', 'ен', ' Ы', 'н', 'мен', ' осы', ' күз', 'де', ' қайта', ' кездес', 'кі', 'сі', ' келеді']
```

In cl100k_base the counts are: KZ-03 44 -> 45 (+1), KZ-08 40 -> 43 (+3).

## C. Did it get better?

Tokens per character.

| Language | cl100k_base | o200k_base | Change |
|---|---|---|---|
| kk | 0.760 | 0.319 | −58% |
| ru | 0.466 | 0.267 | −43% |
| en | 0.203 | 0.203 | 0% |

## Written answers

**1. What is the Kazakh tax?**

Kazakh costs 3.75 times more than English in cl100k_base and 1.58 times more in o200k_base (per character).

In money, 1,000 Kazakh sentences cost $0.1667 in cl100k_base and $0.0700 in o200k_base. The same 1,000 English sentences cost $0.0492 in both. So the extra cost of Kazakh is $0.1175 in cl100k_base and $0.0208 in o200k_base.

It changed a lot. The tax went down from 3.75 to 1.58. Kazakh tokens went down from 200 to 84 (−58%). English did not change (59 tokens in both). So the new tokenizer is better for Kazakh, but Kazakh is still more expensive than English.

**2. Why did the models repair kaz_to_rus but struggle with latin_homoglyph?**

In my results this is only partly true. luna, terra and sol fixed both kaz_to_rus and latin_homoglyph. Five of six models fixed the homoglyph rows (only nemotron struggled). kaz_to_rus was not easy either for the weaker models: nex and nemotron got only one of two kaz_to_rus sentences exact, and laguna got none, sometimes inventing a wrong real word (nex: "елшісінен" → "елшілерінен"; laguna: "сенім" → "сәнiм", "бірқатар" → "бірнеше").

What the model received, by tokens:
- latin_homoglyph: in KZ-03 the word "Алаяқтарға" is 4 tokens (`А | лая | қ | тарға`), and 8 after the homoglyph (`A | л | a | я | қ | t | ар | ға`). The bigger tokens `лая` and `тарға` are gone, and Latin `A`, `a`, `t` are different tokens from Cyrillic `А`, `а`, `т`. The model receives broken pieces, not the same word with one wrong letter.
- kaz_to_rus: the text stays Cyrillic and token counts do not grow (KZ-01 28 -> 26, KZ-07 22 -> 21). The model receives a normal-looking word, with no broken tokens.

But normal-looking tokens did not guarantee a correct fix: weaker models still invented wrong words on kaz_to_rus sentences. So the token stream explains why the homoglyph forces a harder reconstruction problem (broken pieces vs. a whole word), but it does not fully explain why kaz_to_rus was still hard for the weakest models — that looks more like a limit of the model itself than of the tokenizer. Token streams show what the model received, not why it made a mistake.

**3. Name one thing this measurement does not explain about your Sublab Medium results.**

It does not explain the three models that are not from OpenAI (nex-n2.5-mini, laguna-s-2.1, nemotron-3-ultra). I measured only OpenAI tokenizers. The other models have their own tokenizers, so their tokens can be very different. My token streams cannot explain their results.

To close the gap, I would use the tokenizers of those models (if they are public), or read `usage.prompt_tokens` from the API answer for the same texts.