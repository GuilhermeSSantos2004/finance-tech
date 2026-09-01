"""Classifier combining noisy text and structured transaction context."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

import joblib
from sklearn.feature_extraction import DictVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import FeatureUnion, Pipeline

from finance_classifier.features import StructuredFeatureExtractor, TextFeatureExtractor


MODEL_VERSION = "0.1.0"
LABEL_BUSINESS = "BUSINESS"
LABEL_PERSONAL = "PERSONAL"
LABEL_REVIEW = "REVIEW"


@dataclass(frozen=True)
class ClassificationResult:
    classification: str
    model_class: str
    probability_business: float
    probability_personal: float
    confidence: float
    requires_review: bool
    model_version: str = MODEL_VERSION

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        return {
            "classification": payload["classification"],
            "modelClass": payload["model_class"],
            "probabilities": {
                "BUSINESS": payload["probability_business"],
                "PERSONAL": payload["probability_personal"],
            },
            "confidence": payload["confidence"],
            "requiresReview": payload["requires_review"],
            "modelVersion": payload["model_version"],
        }


def build_pipeline(*, random_state: int = 42) -> Pipeline:
    text_pipeline = Pipeline(
        steps=[
            ("extract", TextFeatureExtractor()),
            (
                "tfidf",
                TfidfVectorizer(
                    analyzer="char_wb",
                    ngram_range=(3, 5),
                    min_df=1,
                    max_features=75_000,
                    sublinear_tf=True,
                    lowercase=False,
                ),
            ),
        ]
    )
    structured_pipeline = Pipeline(
        steps=[
            ("extract", StructuredFeatureExtractor()),
            ("vectorize", DictVectorizer(sparse=True)),
        ]
    )
    features = FeatureUnion(
        transformer_list=[
            ("text", text_pipeline),
            ("structured", structured_pipeline),
        ]
    )
    return Pipeline(
        steps=[
            ("features", features),
            (
                "classifier",
                LogisticRegression(
                    C=2.0,
                    class_weight="balanced",
                    max_iter=2_000,
                    random_state=random_state,
                    solver="liblinear",
                ),
            ),
        ]
    )


class TransactionClassifier:
    """Binary model with an abstention zone for low-confidence predictions."""

    def __init__(
        self,
        *,
        personal_threshold: float = 0.20,
        business_threshold: float = 0.80,
        random_state: int = 42,
    ) -> None:
        if not 0.0 < personal_threshold < business_threshold < 1.0:
            raise ValueError("Thresholds devem obedecer 0 < personal < business < 1")
        self.personal_threshold = personal_threshold
        self.business_threshold = business_threshold
        self.random_state = random_state
        self.pipeline = build_pipeline(random_state=random_state)

    def fit(
        self,
        transactions: Sequence[Mapping[str, Any]],
        labels: Sequence[str],
    ) -> "TransactionClassifier":
        normalized_labels = [str(label).upper() for label in labels]
        if len(transactions) != len(normalized_labels):
            raise ValueError("Quantidade de transacoes e rotulos deve ser igual")
        if set(normalized_labels) != {LABEL_BUSINESS, LABEL_PERSONAL}:
            raise ValueError("Treinamento requer as classes BUSINESS e PERSONAL")
        self.pipeline.fit(list(transactions), normalized_labels)
        return self

    @property
    def classes_(self) -> list[str]:
        return [str(label) for label in self.pipeline.named_steps["classifier"].classes_]

    def predict_business_probability(
        self, transactions: Sequence[Mapping[str, Any]]
    ) -> list[float]:
        probabilities = self.pipeline.predict_proba(list(transactions))
        business_index = self.classes_.index(LABEL_BUSINESS)
        return [float(row[business_index]) for row in probabilities]

    def predict_one(self, transaction: Mapping[str, Any]) -> ClassificationResult:
        probability_business = self.predict_business_probability([transaction])[0]
        probability_personal = 1.0 - probability_business
        model_class = LABEL_BUSINESS if probability_business >= 0.5 else LABEL_PERSONAL

        if probability_business >= self.business_threshold:
            classification = LABEL_BUSINESS
        elif probability_business <= self.personal_threshold:
            classification = LABEL_PERSONAL
        else:
            classification = LABEL_REVIEW

        return ClassificationResult(
            classification=classification,
            model_class=model_class,
            probability_business=round(probability_business, 6),
            probability_personal=round(probability_personal, 6),
            confidence=round(max(probability_business, probability_personal), 6),
            requires_review=classification == LABEL_REVIEW,
        )

    def predict_many(
        self, transactions: Sequence[Mapping[str, Any]]
    ) -> list[ClassificationResult]:
        probabilities = self.predict_business_probability(transactions)
        results = []
        for probability_business in probabilities:
            probability_personal = 1.0 - probability_business
            model_class = LABEL_BUSINESS if probability_business >= 0.5 else LABEL_PERSONAL
            if probability_business >= self.business_threshold:
                classification = LABEL_BUSINESS
            elif probability_business <= self.personal_threshold:
                classification = LABEL_PERSONAL
            else:
                classification = LABEL_REVIEW
            results.append(
                ClassificationResult(
                    classification=classification,
                    model_class=model_class,
                    probability_business=round(probability_business, 6),
                    probability_personal=round(probability_personal, 6),
                    confidence=round(max(probability_business, probability_personal), 6),
                    requires_review=classification == LABEL_REVIEW,
                )
            )
        return results

    def save(self, path: str | Path) -> Path:
        destination = Path(path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(self, destination)
        return destination

    @classmethod
    def load(cls, path: str | Path) -> "TransactionClassifier":
        loaded = joblib.load(Path(path))
        if not isinstance(loaded, cls):
            raise TypeError("Artefato nao contem um TransactionClassifier valido")
        return loaded

