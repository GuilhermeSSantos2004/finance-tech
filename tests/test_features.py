from __future__ import annotations

import unittest
from pathlib import Path

from finance_classifier.data import load_training_data
from finance_classifier.features import compose_text, structured_features


ROOT = Path(__file__).resolve().parents[1]
BUSINESS = ROOT / "data/synthetic/transacoes_comerciais_30.json"
PERSONAL = ROOT / "data/synthetic/transacoes_pessoais_30.json"


class FeatureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.records, _, _ = load_training_data([BUSINESS, PERSONAL])

    def test_text_does_not_include_document_or_target(self) -> None:
        record = self.records[0]
        text = compose_text(record)
        document = record["businessContext"]["documentNumber"]["value"]
        self.assertNotIn(document, text)
        self.assertNotIn("BUSINESS", text)

    def test_structured_features_exclude_identifiers(self) -> None:
        features = structured_features(self.records[0])
        self.assertNotIn("id", features)
        self.assertNotIn("accountId", features)
        self.assertNotIn("target", features)
        self.assertIn("main_cnae", features)
        self.assertIn("amount_log1p", features)


if __name__ == "__main__":
    unittest.main()

