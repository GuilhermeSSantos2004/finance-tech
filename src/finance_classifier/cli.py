"""Command line interface for training and local inference."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from finance_classifier.data import extract_transactions, load_training_data
from finance_classifier.model import TransactionClassifier
from finance_classifier.training import train_and_save


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="finance-classifier",
        description="Classifica transacoes de MEI como comerciais ou pessoais.",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    train = commands.add_parser("train", help="Treina e avalia o classificador")
    train.add_argument("--business", required=True, type=Path)
    train.add_argument("--personal", required=True, type=Path)
    train.add_argument("--output", type=Path, default=Path("artifacts"))
    train.add_argument("--test-size", type=float, default=0.25)
    train.add_argument("--random-state", type=int, default=42)

    predict = commands.add_parser("predict", help="Classifica uma ou mais transacoes")
    predict.add_argument("--model", required=True, type=Path)
    predict.add_argument("--input", required=True, type=Path)
    predict.add_argument("--output", type=Path)
    return parser


def _train(args: argparse.Namespace) -> int:
    transactions, labels, groups = load_training_data([args.business, args.personal])
    result = train_and_save(
        transactions,
        labels,
        groups,
        output_dir=args.output,
        test_size=args.test_size,
        random_state=args.random_state,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def _predict(args: argparse.Namespace) -> int:
    payload = json.loads(args.input.read_text(encoding="utf-8"))
    transactions = extract_transactions(payload, source=str(args.input))
    classifier = TransactionClassifier.load(args.model)
    predictions = []
    for transaction, prediction in zip(transactions, classifier.predict_many(transactions)):
        predictions.append({"id": transaction.get("id"), **prediction.to_dict()})
    result = {"predictions": predictions}
    serialized = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(serialized, encoding="utf-8")
    else:
        print(serialized, end="")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.command == "train":
        return _train(args)
    if args.command == "predict":
        return _predict(args)
    raise AssertionError("Comando nao tratado")


if __name__ == "__main__":
    raise SystemExit(main())

