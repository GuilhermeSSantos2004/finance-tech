from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from finance_classifier.data import load_training_directory
from finance_classifier.model import TransactionClassifier
from finance_classifier.training import train_and_save


ROOT = Path(__file__).resolve().parents[1]
TRAINING_DIR = ROOT / "data/training"


class ModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.records, cls.labels, cls.groups = load_training_directory(TRAINING_DIR)

    def test_fit_predict_save_and_load(self) -> None:
        classifier = TransactionClassifier().fit(self.records, self.labels)
        result = classifier.predict_one(self.records[0])
        self.assertIn(result.classification, {"BUSINESS", "PERSONAL", "REVIEW"})
        self.assertGreaterEqual(result.probability_business, 0.0)
        self.assertLessEqual(result.probability_business, 1.0)

        with tempfile.TemporaryDirectory() as directory:
            path = classifier.save(Path(directory) / "model.joblib")
            loaded = TransactionClassifier.load(path)
            loaded_result = loaded.predict_one(self.records[0])
            self.assertEqual(result.to_dict(), loaded_result.to_dict())

    def test_training_generates_metrics_without_group_overlap(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = train_and_save(
                self.records,
                self.labels,
                self.groups,
                output_dir=directory,
                random_state=42,
            )
            self.assertTrue(Path(result["model"]).exists())
            self.assertTrue(Path(result["metrics"]).exists())
            self.assertEqual(result["evaluation"]["split"]["groupOverlap"], [])
            self.assertIn("balancedAccuracy", result["evaluation"]["metrics"])


if __name__ == "__main__":
    unittest.main()

