"""Sample the Golden Set from ABCD and hand-label it in the terminal.

Usage (from the repo root):
    uv run python src/dataset_script/golden_labeler.py                # label (samples on first run)
    uv run python src/dataset_script/golden_labeler.py --sample-only  # only create the sample
    uv run python src/dataset_script/golden_labeler.py --stats        # progress and verdict counts
    uv run python src/dataset_script/golden_labeler.py --pass 2 --n 30  # intra-rater re-label
"""

import argparse
import ast
import json
import random
import re
import shutil
import textwrap
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

from autoqa.guidelines import SUBFLOW_MAP, load_guidelines, guideline_key

ROOT = Path(__file__).resolve().parents[2]
ABCD_PATH = ROOT / "data" / "abcd_v1.1.json"
GUIDELINES_PATH = ROOT / "data" / "guidelines.json"
RUBRIC_PATH = ROOT / "rubric.md"
GOLDEN_DIR = ROOT / "data" / "golden"

GOLDEN_VERSION = "v0.1"
SAMPLE_PATH = GOLDEN_DIR / f"sample_{GOLDEN_VERSION}.jsonl"
PASS2_IDS_PATH = GOLDEN_DIR / f"pass2_ids_{GOLDEN_VERSION}.json"

SEED = 42
SAMPLE_SIZE = 150
PER_POLICY_SUBFLOW = 4
PER_OTHER_SUBFLOW = 2
PILOT_SIZE = 20
# 15 slots -> 3 train / 4 dev / 8 test, interleaved so every subflow is spread across splits.
SPLIT_PATTERN = ["test", "dev", "test", "train", "test", "dev", "test", "test",
                 "train", "dev", "test", "test", "train", "dev", "test"]

VERDICTS = {"p": "PASS", "f": "FAIL", "n": "NOT_APPLICABLE"}

FAQ_PREFIXES = {
    "single_item_query": {"boots": "Boots FAQ", "shirt": "Shirt FAQ", "jeans": "Jeans FAQ", "jacket": "Jacket FAQ"},
    "storewide_query": {"pricing": "Pricing FAQ", "membership": "Membership FAQ",
                        "timing": "Timing FAQ", "policy": "Policy FAQ"},
}
FAQ_FLOWS = {"single_item_query": "Single-Item Query", "storewide_query": "Storewide Query"}

# Subflows whose guidelines contain a decision rule that policy_followed can judge.
POLICY_SUBFLOWS = {
    ("Product Defect", "Return Due to Stain"), ("Product Defect", "Return Due to Color"),
    ("Product Defect", "Return Due to Size"), ("Product Defect", "Update Refund"),
    ("Order Issue", "Status Mystery Fee"), ("Order Issue", "Manage Upgrade"),
    ("Order Issue", "Manage Downgrade"), ("Order Issue", "Manage Create"), ("Order Issue", "Manage Cancel"),
    ("Purchase Dispute", "Bad Price Competitor"), ("Purchase Dispute", "Bad Price Yesterday"),
    ("Purchase Dispute", "Promo Code Invalid"), ("Purchase Dispute", "Promo Code Out of Date"),
    ("Purchase Dispute", "Mistimed Billing Already Returned"), ("Purchase Dispute", "Mistimed Billing Never Bought"),
    ("Shipping Issue", "Missing Item"),
    ("Subscription Inquiry", "Manage Extension"), ("Subscription Inquiry", "Manage Dispute Bill"),
}


# ---------------------------------------------------------------- sampling

def build_sample(guidelines: dict) -> list[dict]:
    for flow, subflow in list(SUBFLOW_MAP.values()) + list(POLICY_SUBFLOWS):
        assert subflow in guidelines[flow]["subflows"], f"Not in guidelines.json: {flow} / {subflow}"

    print(f"Loading {ABCD_PATH.name} ...")
    with open(ABCD_PATH) as f:
        abcd = json.load(f)

    pool = defaultdict(list)  # guideline key -> conversations
    for abcd_split, convos in abcd.items():
        for c in convos:
            key = guideline_key(c["scenario"]["flow"], c["scenario"]["subflow"])
            if key is not None:
                pool[key].append({**c, "abcd_split": abcd_split})

    all_keys = {(f, s) for f, fv in guidelines.items() for s in fv["subflows"]}
    assert set(pool) == all_keys, f"Subflows with no conversations: {all_keys - set(pool)}"

    rng = random.Random(SEED)
    chosen = []
    for key in sorted(pool):
        k = PER_POLICY_SUBFLOW if key in POLICY_SUBFLOWS else PER_OTHER_SUBFLOW
        chosen += [(key, c) for c in rng.sample(pool[key], k)]
    picked = {c["convo_id"] for _, c in chosen}
    rest = [(key, c) for key in sorted(pool) for c in pool[key] if c["convo_id"] not in picked]
    chosen += rng.sample(rest, SAMPLE_SIZE - len(chosen))

    # Golden split, stratified: walk the sample subflow by subflow through the interleaved pattern.
    chosen.sort(key=lambda kc: (kc[0], rng.random()))
    split_of = {c["convo_id"]: SPLIT_PATTERN[i % len(SPLIT_PATTERN)] for i, (_, c) in enumerate(chosen)}

    # Labeling order: round-robin across flows, so the pilot covers every flow.
    by_flow = defaultdict(list)
    for key, c in chosen:
        by_flow[key[0]].append((key, c))
    flows = sorted(by_flow)
    rng.shuffle(flows)
    for f in flows:
        rng.shuffle(by_flow[f])
    ordered = []
    while any(by_flow.values()):
        for f in flows:
            if by_flow[f]:
                ordered.append(by_flow[f].pop())

    return [{
        "order": i + 1,
        "convo_id": c["convo_id"],
        "abcd_split": c["abcd_split"],
        "flow": c["scenario"]["flow"],
        "subflow": c["scenario"]["subflow"],
        "guideline_flow": key[0],
        "guideline_subflow": key[1],
        "golden_split": split_of[c["convo_id"]],
        "pilot": i < PILOT_SIZE,
        "provenance": "real",
        "scenario": c["scenario"],
        "original": c["original"],
    } for i, (key, c) in enumerate(ordered)]


def load_or_create_sample(guidelines: dict, resample: bool) -> list[dict]:
    if SAMPLE_PATH.exists() and not resample:
        with open(SAMPLE_PATH) as f:
            return [json.loads(line) for line in f]
    if SAMPLE_PATH.exists() and any(GOLDEN_DIR.glob("labels_*.jsonl")):
        raise SystemExit("Labels already exist for this sample; refusing to resample. Move them away first.")
    sample = build_sample(guidelines)
    GOLDEN_DIR.mkdir(parents=True, exist_ok=True)
    with open(SAMPLE_PATH, "w") as f:
        for rec in sample:
            f.write(json.dumps(rec) + "\n")
    print(f"Wrote {len(sample)} conversations to {SAMPLE_PATH.relative_to(ROOT)}")
    return sample


def print_sample_summary(sample: list[dict]) -> None:
    splits = Counter(r["golden_split"] for r in sample)
    subflows = {(r["guideline_flow"], r["guideline_subflow"]) for r in sample}
    policy = sum((r["guideline_flow"], r["guideline_subflow"]) in POLICY_SUBFLOWS for r in sample)
    print(f"  conversations: {len(sample)}   subflows covered: {len(subflows)}   policy-subflow chats: {policy}")
    print(f"  splits: " + ", ".join(f"{s}={splits[s]}" for s in ("train", "dev", "test")))
    print(f"  pilot: {sum(r['pilot'] for r in sample)}   flows in pilot: "
          f"{len({r['guideline_flow'] for r in sample if r['pilot']})}")


# ---------------------------------------------------------------- rubric

def load_rubric() -> tuple[str, list[dict]]:
    text = RUBRIC_PATH.read_text()
    m = re.search(r"^# .*?(v\d+(?:\.\d+)*)\s*$", text, re.M)
    if not m:
        raise SystemExit("rubric.md needs a title with a version, e.g. '# ABCD Rubric v0.1'")
    criteria = []
    for block in re.split(r"^## ", text, flags=re.M)[1:]:
        name = block.split("\n", 1)[0].strip()
        question = re.search(r"\*\*Question:\*\*\s*(.+)", block)
        na = re.search(r"\*\*N/A:\*\*\s*(.+)", block)
        criteria.append({
            "name": name,
            "question": question.group(1).strip() if question else "",
            "allows_na": not (na and "never NOT_APPLICABLE" in na.group(1)),
        })
    return m.group(1), criteria


# ---------------------------------------------------------------- display

def wrap(text: str, indent: int) -> str:
    width = max(60, shutil.get_terminal_size().columns - 2)
    return textwrap.fill(text, width=width, initial_indent=" " * indent,
                         subsequent_indent=" " * indent).lstrip() if text else ""


def show_conversation(rec: dict, position: str, guidelines: dict) -> None:
    line = "=" * min(100, shutil.get_terminal_size().columns)
    tag = " · PILOT" if rec["pilot"] else ""
    print(f"\n{line}\nChat {position} · #{rec['convo_id']} · {rec['guideline_flow']} / "
          f"{rec['guideline_subflow']} · split={rec['golden_split']}{tag}\n{line}")

    for i, (speaker, text) in enumerate(rec["original"]):
        label = "  [action]" if speaker == "action" else speaker
        print(f"{i:3} {label:10} {wrap(text, 15)}")

    passage = guidelines[rec["guideline_flow"]]["subflows"][rec["guideline_subflow"]]
    print(f"\n--- Guidelines: {rec['guideline_flow']} / {rec['guideline_subflow']} ---")
    for instr in passage["instructions"]:
        print(f"  * {wrap(instr, 4)}")
    for n, action in enumerate(passage["actions"], 1):
        print(f"  {n}. [{action['button']}] {wrap(action['text'], 6)}")
        for sub in action["subtext"]:
            print(f"       - {wrap(sub, 9)}")

    print("\n--- HIDDEN: scenario data, not visible to the Grader ---")
    for group in ("personal", "order", "product"):
        for k, v in rec["scenario"].get(group, {}).items():
            if k == "products" and isinstance(v, str):
                try:
                    v = ", ".join(f"{p['brand']} {p['product_type']} ${p['amount']}" for p in ast.literal_eval(v))
                except (ValueError, SyntaxError, KeyError):
                    pass
            if k != "image_url":
                print(f"  {group}.{k}: {v}")
    print(line)


# ---------------------------------------------------------------- labeling

class Redo(Exception):
    pass


class Skip(Exception):
    pass


class Quit(Exception):
    pass


def ask(prompt: str) -> str:
    try:
        return input(prompt).strip()
    except (EOFError, KeyboardInterrupt):
        raise Quit


def label_conversation(rec: dict, criteria: list[dict]) -> list[dict]:
    labels = []
    for crit in criteria:
        options = "p/f/n" if crit["allows_na"] else "p/f"
        print(f"\n{crit['name']}: {crit['question']}")
        while True:
            answer = ask(f"  verdict [{options}]  (r=redo chat, s=skip, q=quit): ").lower()
            if answer == "r":
                raise Redo
            if answer == "s":
                raise Skip
            if answer == "q":
                raise Quit
            if answer in VERDICTS and (answer != "n" or crit["allows_na"]):
                break
            print(f"  -> enter one of: {options}" + ("" if crit["allows_na"] else " (N/A is not allowed here)"))
        reason = ask("  reason / quote (optional): ")
        unsure = ask("  unsure? [y/N]: ").lower() == "y"
        labels.append({"criterion": crit["name"], "verdict": VERDICTS[answer],
                       "reason": reason, "unsure": unsure})
    return labels


def read_labels(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]


def done_ids(labels: list[dict], pass_no: int, criteria: list[dict]) -> set[int]:
    names = {c["name"] for c in criteria}
    seen = defaultdict(set)
    for lab in labels:
        if lab["pass_no"] == pass_no:
            seen[lab["convo_id"]].add(lab["criterion"])
    return {cid for cid, crits in seen.items() if names <= crits}


def pass2_queue(sample: list[dict], labels: list[dict], criteria: list[dict], n: int) -> list[dict]:
    """The re-label set is chosen once and stored, so resuming pass 2 keeps the same chats."""
    if PASS2_IDS_PATH.exists():
        ids = json.loads(PASS2_IDS_PATH.read_text())
    else:
        labeled = sorted(done_ids(labels, 1, criteria))
        if len(labeled) < n:
            raise SystemExit(f"Only {len(labeled)} chats are labeled in pass 1; need {n} for pass 2.")
        ids = random.Random(SEED + 2).sample(labeled, n)
        PASS2_IDS_PATH.write_text(json.dumps(ids))
    by_id = {r["convo_id"]: r for r in sample}
    return [by_id[i] for i in ids]


def run_labeling(sample, guidelines, version, criteria, pass_no, n) -> None:
    labels_path = GOLDEN_DIR / f"labels_{version}.jsonl"
    labels = read_labels(labels_path)
    queue = sample if pass_no == 1 else pass2_queue(sample, labels, criteria, n)
    done = done_ids(labels, pass_no, criteria)
    skipped = set()
    print(f"Rubric {version} · {len(criteria)} criteria · pass {pass_no} · "
          f"{len(done & {r['convo_id'] for r in queue})}/{len(queue)} done · labels -> {labels_path.relative_to(ROOT)}")

    while True:
        todo = [r for r in queue if r["convo_id"] not in done and r["convo_id"] not in skipped]
        if not todo:
            print("\nNothing left to label" + (" (some chats were skipped this session)." if skipped else "."))
            return
        rec = todo[0]
        position = f"{queue.index(rec) + 1}/{len(queue)}"
        show_conversation(rec, position, guidelines)
        try:
            chat_labels = label_conversation(rec, criteria)
        except Redo:
            continue
        except Skip:
            skipped.add(rec["convo_id"])
            continue
        except Quit:
            print("\nQuit. This chat was not saved; everything before it is.")
            return

        now = datetime.now(timezone.utc).isoformat(timespec="seconds")
        with open(labels_path, "a") as f:
            for lab in chat_labels:
                f.write(json.dumps({"convo_id": rec["convo_id"], **lab, "rubric_version": version,
                                    "pass_no": pass_no, "labeled_at": now}) + "\n")
        done.add(rec["convo_id"])
        print(f"  saved #{rec['convo_id']} ({len(done & {r['convo_id'] for r in queue})}/{len(queue)})")
        if pass_no == 1 and len(done) == PILOT_SIZE:
            print("\n*** Pilot done (20 chats). Review your 'unsure' notes and update rubric.md before continuing. ***")
            if ask("Continue labeling now? [y/N]: ").lower() != "y":
                return


def print_stats(sample, version, criteria) -> None:
    labels = read_labels(GOLDEN_DIR / f"labels_{version}.jsonl")
    for pass_no in (1, 2):
        rows = [lab for lab in labels if lab["pass_no"] == pass_no]
        if not rows:
            continue
        total = len(sample) if pass_no == 1 else len(json.loads(PASS2_IDS_PATH.read_text()))
        print(f"\nPass {pass_no}: {len(done_ids(labels, pass_no, criteria))}/{total} chats labeled "
              f"(rubric {version}), {sum(lab['unsure'] for lab in rows)} unsure labels")
        print(f"  {'criterion':24} {'PASS':>5} {'FAIL':>5} {'N/A':>5}")
        for crit in criteria:
            c = Counter(lab["verdict"] for lab in rows if lab["criterion"] == crit["name"])
            print(f"  {crit['name']:24} {c['PASS']:5} {c['FAIL']:5} {c['NOT_APPLICABLE']:5}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--sample-only", action="store_true", help="create the sample and exit")
    parser.add_argument("--resample", action="store_true", help="rebuild the sample (only if no labels exist)")
    parser.add_argument("--stats", action="store_true", help="show progress and verdict counts")
    parser.add_argument("--pass", dest="pass_no", type=int, choices=(1, 2), default=1,
                        help="1 = first labeling, 2 = intra-rater re-label")
    parser.add_argument("--n", type=int, default=30, help="chats to re-label in pass 2")
    args = parser.parse_args()

    guidelines = load_guidelines()
    sample = load_or_create_sample(guidelines, args.resample)
    if args.sample_only:
        print_sample_summary(sample)
        return
    version, criteria = load_rubric()
    if args.stats:
        print_stats(sample, version, criteria)
        return
    run_labeling(sample, guidelines, version, criteria, args.pass_no, args.n)


if __name__ == "__main__":
    main()
