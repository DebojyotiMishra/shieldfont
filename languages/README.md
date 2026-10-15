# Languages

Each language ShieldFont supports, or is working towards, has one folder here,
named by its language code: `en/`, `fr/`, later `pt/`, `es/`. Everything that is
specific to that language lives in its folder. Tools that work for any language
stay where they are:

| Lives in `languages/<code>/` | Stays shared |
|---|---|
| The script that builds the word pairs | `scripts/generate_font.py` (builds a font from any word list) |
| The word pairs and the flat word list a font is built from | `scripts/reseed_mapping.py` (reshuffles any pairs file) |
| The native-speaker review sheet | `scripts/check_pairs.py` (checks any pairs file) |
| Benchmark results for this language | `scripts/subset_font.py`, `scripts/audit_font.py` |
| Encoder tests that use this language's word list | `packages/core` (the encoder, which never knows the language) |

To start a new language, copy `_template/` to `languages/<code>/` and fill it in.

## Inside a language folder

```text
languages/<code>/
├── README.md        what was built, the grammar rules it handles, known gaps
├── language.json    status, inputs and numbers, in the same shape for every language
├── build/           the script that makes the word pairs (+ .cache/, gitignored)
├── data/            pairs_<id>.json and <id>_for_font.json
├── audit/           the review sheet for a native speaker
├── benchmarks/      measured results for this language
└── tests/           encoder tests run against data/
```

A folder only needs the parts it has reached. English's files have not moved
in yet; `en/README.md` lists where each one lives today. French (PR #12,
issue #11) is being rebuilt before its folder lands here.

File names keep the language code (`pairs_fr_v1_alpha.json`), so a file copied
out of its folder still says which language it is.

## From first draft to shipped

`status` in `language.json` is one of three values.

| Status | What has to be true |
|---|---|
| `building` | A build script reproduces the pairs from a fixed seed, and the pairs pass `scripts/check_pairs.py`. Pairs are in the shared format, so `scripts/reseed_mapping.py --pairs` works on them unchanged. |
| `candidate` | All three of: the `numbers` block is filled in, measured on real text in this language with this language's own tools (a single sample paragraph does not count); a native speaker has filled in the review sheet, at least for the rows the build marks as risky; and every entry in `inputs` has `license_approved: true`. |
| `shipped` | A font has been built from the word list, and the mapping is in `packages/core/src/mappings/` with `_meta.lang` set. |

Measuring and native review can happen in either order. `numbers` and `review`
in `language.json` track them separately.

A word list never ships without its font. Without the font, readers see the
decoy words on screen instead of the real ones.

## How a language's word pairs get built

Every language builds its pairs the same way. It sorts words into groups that
are grammatically interchangeable (a "bucket"), shuffles each group with a
seed, pairs neighbours, and rejects pairs whose meanings are too close. What
changes between languages is the inputs, not the method.

Each language supplies:

1. **A dictionary reader.** It returns every word form with its part of
   speech, base form, grammar features and frequency. English reads wordfreq,
   spaCy and pyinflect. The first French draft read Lexique.
2. **A bucket rule.** Given a word, it returns the group it can be swapped
   within, or nothing if the word is ambiguous. This is where each language's
   grammar lives. English groups nouns by meaning class, concreteness and
   number. French adds gender and whether the word starts with a vowel sound
   (`l'arbre` against `le héros`).
3. **A meaning model.** These are word vectors used to reject pairs that are
   too close in meaning, and optionally to split buckets into topic clusters.
4. **Lists.** Words that must never be swapped (like French `pas`, which would
   flip sentences to negative), and hand-made pairs (months, numbers).
5. **Settings worth trying.** Each one is a named filter with a few values, for
   example the similarity cutoff or the cluster size.
6. **Scoring resources.** These are real text in the language, a language
   model for fluency, a quality filter, and a sentence-embedding model for
   meaning change.

Shared, the same for every language:

- the shuffle-and-pair step and the meaning checks
- `scripts/check_pairs.py`, which every pairs file must pass. It checks that
  every entry has its reverse, that no word sits in two pairs, and that both
  words in a pair share a bucket.
- `scripts/reseed_mapping.py`, the pairs file format, and the font builder

### Two rules English taught us

**Run the checks again after any step that re-pairs words.** English's source
pairs (`benchmark/data/v7/pairs_v7_alpha_v15_0_1_0_0_0_0.json`) were re-paired
by a late filter (K6, which re-ranks pairs by how natural they sound) after the
meaning checks had already run. For 5,709 of its 5,962 pairs, the stored
partner details belong to a word the pair no longer contains, and 7 synonym
pairs and 1 pair of opposites got through. `check_pairs.py` also finds 12 words
that each sit in two pairs and 8 pairs whose words come from different buckets.
Flattening kept one partner per word, so the shipped mapping still swaps both
ways, but the 7 synonym pairs and the pair of opposites ship.

**Try a few settings, not hundreds.** English compared hundreds of setting
combinations, scoring each on meaning change, words changed, fluency and how
much a quality filter keeps. The pick still came down to a human reading the
output, and nothing tested after v15 replaced it. For a new language, compare
a handful of combinations of the settings that actually moved English: bucket
detail, the similarity cutoff, the near-neighbour count, cluster size, and the
never-swap list. Then have a native speaker read the best two or three.

## Licensing

Code and word lists in this repo ship under AGPL-3.0. (Fonts have their own
licenses; see `NOTICE`.) Before a language ships or is re-released, the
maintainer approves the license of every data source its build reads.
`inputs` in `language.json` records each source, what the build uses it for,
its license, and whether it is approved.

### Not decided yet

- The pass marks for `numbers` and for the native review. English's numbers
  are the reference point, not the bar: French changes fewer words per
  sentence because it has more word forms, so the same bar may not fit.
- The measuring tools are English-only today (an English KenLM,
  English-trained filters). Each language needs its own before it can become
  a `candidate`.
- How a shipped non-English mapping is named in npm. The likely form is
  `fr-alpha.json` next to today's `alpha.json`.

## Running a language's tests

Tests in `languages/<code>/tests/` import the encoder from `packages/core/src`.
The core package's test config includes them, so `npm test` runs them:

```ts
// packages/core/vitest.config.ts
test: {
  dir: "../..",
  include: ["packages/core/test/**/*.test.ts", "languages/*/tests/**/*.test.ts"],
}
```
