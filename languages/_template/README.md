# <Language name> mapping: `<code>-v1-alpha`

Status: `building`. Does not ship (see `../README.md` for the four steps).

| | |
|---|---|
| Logical pairs | |
| Seed | |
| Dictionary used | name, license, link |
| Build script | `build/build_pairs.py` |
| Flat word list for the font | `data/<code>_v1_alpha_for_font.json` |

## Grammar this language needs that English does not

List each rule that a careless swap would break, with one example of the broken
output. For French that was gender (`la maison` turning into `la livre`) and
elision (`l'arbre` turning into `l'maison`). Say how the build keeps each rule.

## What is not here yet

Missing benchmarks, missing review, words left out on purpose and why.

## Reproducing

The exact commands, from a clean checkout, to rebuild `data/` byte for byte.
