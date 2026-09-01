from __future__ import annotations

import unittest
from pathlib import Path

from finance_classifier.data import load_training_data
from finance_classifier.training import group_split_indices


ROOT = Path(__file__).resolve().parents[1]
BUSINESS = ROOT / "data/synthetic/transacoes_comerciais_30.json"
PERSONAL = ROOT / "data/synthetic/transacoes_pessoais_30.json"


class DatasetTests(unittest.TestCase):
    def test_balanced_dataset_loads(self) -> None:
        records, labels, groups = load_training_data([BUSINESS, PERSONAL])
        self.assertEqual(len(records), 60)
        self.assertEqual(labels.count("BUSINESS"), 30)
        self.assertEqual(labels.count("PERSONAL"), 30)
        self.assertEqual(len(set(groups)), 6)

    def test_group_split_has_no_account_leakage(self) -> None:
        _, labels, groups = load_training_data([BUSINESS, PERSONAL])
        train, test = group_split_indices(labels, groups, test_size=0.25, random_state=42)
        train_groups = {groups[index] for index in train}
        test_groups = {groups[index] for index in test}
        self.assertFalse(train_groups.intersection(test_groups))
        self.assertEqual({labels[index] for index in train}, {"BUSINESS", "PERSONAL"})
        self.assertEqual({labels[index] for index in test}, {"BUSINESS", "PERSONAL"})


if __name__ == "__main__":
    unittest.main()

