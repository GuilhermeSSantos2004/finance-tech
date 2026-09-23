from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def safe_div(a: int, b: int) -> float:
    return round(a / b, 4) if b else 0.0


def summarize(rows):
    total = len(rows)
    auto = [r for r in rows if r["classification"] in {"BUSINESS", "PERSONAL"}]
    reviews = [r for r in rows if r["classification"] == "REVIEW"]
    auto_correct = [r for r in auto if r["classification"] == r["expected"]]
    auto_errors = [r for r in auto if r["classification"] != r["expected"]]
    model_correct = [r for r in rows if r.get("modelClass") == r["expected"]]
    strict_correct = [r for r in rows if r["classification"] == r["expected"]]
    return {
        "records": total,
        "strictAccuracy": safe_div(len(strict_correct), total),
        "coverage": safe_div(len(auto), total),
        "reviewRate": safe_div(len(reviews), total),
        "autoDecisionAccuracy": safe_div(len(auto_correct), len(auto)),
        "autoDecisionErrors": len(auto_errors),
        "reviews": len(reviews),
        "binaryModelClassAccuracy": safe_div(len(model_correct), total),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Score finance-tech blind benchmark predictions.")
    ap.add_argument("--predictions", type=Path, required=True, help="JSON produced by finance_classifier predict")
    ap.add_argument("--gold", type=Path, default=Path(__file__).with_name("benchmark_140_gold.json"))
    ap.add_argument("--output", type=Path)
    args = ap.parse_args()

    pred_payload = load_json(args.predictions)
    gold_payload = load_json(args.gold)
    predictions = pred_payload.get("predictions", pred_payload if isinstance(pred_payload, list) else [])
    answers = gold_payload.get("answers", [])

    pred_by_id = {str(p.get("id")): p for p in predictions if p.get("id") is not None}
    gold_by_id = {str(a["id"]): a for a in answers}

    missing = sorted(set(gold_by_id) - set(pred_by_id))
    extra = sorted(set(pred_by_id) - set(gold_by_id))
    if missing:
        raise SystemExit(f"Missing {len(missing)} benchmark predictions; first IDs: {missing[:5]}")

    rows = []
    for tx_id, ans in gold_by_id.items():
        p = pred_by_id[tx_id]
        rows.append({
            "id": tx_id,
            "expected": ans["expectedClassification"],
            "difficulty": ans["difficulty"],
            "scenario": ans.get("scenario"),
            "classification": str(p.get("classification", "")).upper(),
            "modelClass": str(p.get("modelClass", "")).upper(),
            "confidence": p.get("confidence"),
            "probabilities": p.get("probabilities", {}),
            "trap": ans.get("trap"),
        })

    by_difficulty = {}
    for difficulty in ["EASY", "MEDIUM", "HARD", "ADVERSARIAL"]:
        by_difficulty[difficulty] = summarize([r for r in rows if r["difficulty"] == difficulty])

    by_class = {}
    for label in ["BUSINESS", "PERSONAL"]:
        by_class[label] = summarize([r for r in rows if r["expected"] == label])

    confusion = Counter((r["expected"], r["classification"]) for r in rows)
    errors = [r for r in rows if r["classification"] in {"BUSINESS", "PERSONAL"} and r["classification"] != r["expected"]]
    reviews = [r for r in rows if r["classification"] == "REVIEW"]
    modelclass_errors = [r for r in rows if r["modelClass"] != r["expected"]]

    result = {
        "summary": summarize(rows),
        "byDifficulty": by_difficulty,
        "byExpectedClass": by_class,
        "decisionConfusion": {
            f"{exp}->{pred}": count for (exp, pred), count in sorted(confusion.items())
        },
        "counts": {
            "extraPredictionIds": len(extra),
            "autoDecisionErrors": len(errors),
            "reviews": len(reviews),
            "binaryModelClassErrors": len(modelclass_errors),
        },
        "errors": errors,
        "reviewsDetail": reviews,
        "binaryModelClassErrorsDetail": modelclass_errors,
    }

    serialized = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(serialized, encoding="utf-8")
    else:
        print(serialized, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())