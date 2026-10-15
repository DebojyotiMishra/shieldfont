#!/usr/bin/env python3
"""check_pairs.py — the checks every language's word pairs must pass.

Works on any pairs file in the shared schema (`all_pairs: [{src, tgt, bucket,
...}]`), whatever the language. Run it after anything that builds or re-pairs
words: a language's build script, scripts/reseed_mapping.py, or a filter that
re-ranks pairs. A step that re-pairs words after the meaning checks ran
(English's K6 did) leaves pairs nobody checked; this is the gate that catches it.

Hard failures (exit 1):
  - an entry a -> b with no reverse entry b -> a
  - a word that maps to itself, or a duplicate entry
  - a word that sits in more than one pair
  - a pair whose two words sit in different buckets
  - a word that is not NFC-normalised

Warnings (exit 0, or 1 with --strict):
  - a word whose stored frequency differs between the entries that record it
  - stored partner frequencies (src_zipf/tgt_zipf) that do not belong to the
    word's actual partner, meaning the pair was re-formed after it was checked.
    Needs `pip install wordfreq` and --lang.

Usage:
  python3 scripts/check_pairs.py languages/fr/data/pairs_fr_v1_alpha.json --lang fr
  python3 scripts/check_pairs.py benchmark/data/v7/pairs_v7_alpha_v15_0_1_0_0_0_0.json --lang en
"""
import argparse
import json
import sys
import unicodedata
from pathlib import Path


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("pairs", help="pairs file in the shared all_pairs schema")
    ap.add_argument("--lang", help="language code; enables the frequency check (needs wordfreq)")
    ap.add_argument("--strict", action="store_true", help="treat warnings as failures")
    ap.add_argument("--show", type=int, default=5, help="examples to print per problem")
    args = ap.parse_args()

    doc = json.loads(Path(args.pairs).read_text(encoding="utf-8"))
    pairs = doc.get("all_pairs")
    if not isinstance(pairs, list) or not pairs:
        sys.exit(f"[FAIL] {args.pairs}: no all_pairs list")

    fails, warns = {}, {}

    def add(bucket, key, example):
        bucket.setdefault(key, []).append(example)

    partners, bucket_of, entries = {}, {}, set()
    for p in pairs:
        src, tgt = p.get("src"), p.get("tgt")
        if not src or not tgt:
            add(fails, "entry missing src or tgt", p)
            continue
        if src == tgt:
            add(fails, "word maps to itself", src)
        if (src, tgt) in entries:
            add(fails, "duplicate entry", f"{src} -> {tgt}")
        entries.add((src, tgt))
        partners.setdefault(src, set()).add(tgt)
        bucket_of[src] = p.get("bucket")
        for w in (src, tgt):
            if unicodedata.normalize("NFC", w) != w:
                add(fails, "word not NFC-normalised", w)

    for src, tgts in partners.items():
        if len(tgts) > 1:
            add(fails, "word sits in more than one pair", f"{src} -> {' / '.join(sorted(tgts))}")
    for src, tgt in sorted(entries):
        if (tgt, src) not in entries:
            add(fails, "entry has no reverse entry", f"{src} -> {tgt}")
        elif src < tgt and bucket_of.get(src) != bucket_of.get(tgt):
            add(fails, "pair crosses buckets", f"{src} ({bucket_of.get(src)}) / {tgt} ({bucket_of.get(tgt)})")

    # A word's frequency is a fact about the word, so every entry that records
    # it should agree. Disagreement means the details were copied or left over
    # from an earlier partner. Needs no extra packages.
    recorded = {}
    for p in pairs:
        if p.get("special"):
            continue
        for word, key in ((p.get("src"), "src_zipf"), (p.get("tgt"), "tgt_zipf")):
            if word and p.get(key) is not None:
                recorded.setdefault(word, set()).add(p[key])
    for word, values in recorded.items():
        if len(values) > 1:
            add(warns, "a word's stored frequency differs between its entries (details copied or left from an earlier partner)",
                f"{word}: {sorted(values)}")

    logical = {frozenset((p["src"], p["tgt"])): p for p in pairs
               if p.get("src") and p.get("tgt") and not p.get("special")}

    if args.lang:
        try:
            from wordfreq import zipf_frequency
        except ImportError:
            sys.exit("[FAIL] --lang needs wordfreq: pip install wordfreq")
        fit = stale = 0
        for p in logical.values():
            s, t = p.get("src_zipf"), p.get("tgt_zipf")
            if s is None or t is None:
                continue
            za = zipf_frequency(p["src"], args.lang)
            zb = zipf_frequency(p["tgt"], args.lang)
            # Reverse entries may carry the forward entry's numbers, so accept
            # the stored pair in either order.
            if (abs(za - s) <= .02 and abs(zb - t) <= .02) or (abs(zb - s) <= .02 and abs(za - t) <= .02):
                fit += 1
            else:
                stale += 1
                add(warns, "stored partner frequency belongs to a different word (pair re-formed after checks)",
                    f"{p['src']} / {p['tgt']}: stored {s}/{t}, actual {za}/{zb}")
        print(f"[info] frequency check: {fit} of {fit + stale} pairs carry their own partner's numbers")

    print(f"[info] {args.pairs}: {len(pairs):,} entries, {len(logical):,} logical pairs (not counting specials)")
    for title, group, tag in (("FAIL", fails, "FAIL"), ("WARN", warns, "WARN")):
        for key, items in group.items():
            print(f"[{tag}] {len(items):,} x {key}")
            for ex in items[:args.show]:
                print(f"         {ex}")

    if fails or (args.strict and warns):
        sys.exit(1)
    print("[ok] all hard checks pass" + (" (with warnings)" if warns else ""))


if __name__ == "__main__":
    main()
