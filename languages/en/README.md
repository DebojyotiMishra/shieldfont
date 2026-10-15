# English

Status: `shipped`. The only language in a release today. The default mapping is
v18 `alpha`. `MAPPINGS.md` has the full history from M0 to v18.

English's files have not moved into this folder yet. Fonts, npm builds and the
benchmark write-ups all point at their current paths, so they will move in one
release with every reference updated. Until then, this is where each piece
lives:

| Piece | Current path | Path after the move |
|---|---|---|
| Build script for the word pairs | `benchmark/data/v7/scripts/build_pairs.py` | `languages/en/build/build_pairs.py` |
| Word pairs (alpha source) | `benchmark/data/v7/pairs_v7_alpha_v15_0_1_0_0_0_0.json` | `languages/en/data/` |
| Flat word lists for the fonts | `scripts/v18{alpha,beta,gamma}_for_font.json`, `scripts/m15en_for_font.json` | `languages/en/data/` |
| Benchmarks | `benchmark/data/v7/`, `benchmark/data/v8/` | `languages/en/benchmarks/` |
| Shipped mappings | `packages/core/src/mappings/{alpha,beta,gamma,m15en}.json` | stay where they are (npm reads them there) |
