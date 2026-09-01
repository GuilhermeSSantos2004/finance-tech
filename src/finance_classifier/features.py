"""Leakage-safe feature extraction for noisy Brazilian bank descriptions."""

from __future__ import annotations

import math
import re
import unicodedata
from datetime import datetime
from typing import Any, Mapping, Sequence
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from sklearn.base import BaseEstimator, TransformerMixin


SPACE_RE = re.compile(r"\s+")
NON_ALNUM_RE = re.compile(r"[^A-Z0-9]+")


def nested_get(data: Mapping[str, Any], *path: str, default: Any = None) -> Any:
    current: Any = data
    for key in path:
        if not isinstance(current, Mapping) or key not in current:
            return default
        current = current[key]
    return current


def normalize_text(value: Any) -> str:
    if value is None:
        return ""
    decomposed = unicodedata.normalize("NFKD", str(value))
    without_accents = "".join(char for char in decomposed if not unicodedata.combining(char))
    cleaned = NON_ALNUM_RE.sub(" ", without_accents.upper())
    return SPACE_RE.sub(" ", cleaned).strip()


def _counterparty_name(transaction: Mapping[str, Any]) -> str:
    explicit = nested_get(transaction, "counterpartyData", "normalizedName")
    if explicit:
        return str(explicit)

    merchant = nested_get(transaction, "merchant", "name")
    if merchant:
        return str(merchant)

    direction = str(transaction.get("type", "")).upper()
    role = "payer" if direction == "CREDIT" else "receiver"
    return str(nested_get(transaction, "paymentData", role, "name", default="") or "")


def _counterparty_document_type(transaction: Mapping[str, Any]) -> str:
    explicit = nested_get(transaction, "counterpartyData", "documentType")
    if explicit:
        return str(explicit)

    merchant_type = nested_get(transaction, "merchant", "documentNumber", "type")
    if merchant_type:
        return str(merchant_type)

    direction = str(transaction.get("type", "")).upper()
    role = "payer" if direction == "CREDIT" else "receiver"
    return str(
        nested_get(transaction, "paymentData", role, "documentNumber", "type", default="UNKNOWN")
        or "UNKNOWN"
    )


def compose_text(transaction: Mapping[str, Any]) -> str:
    """Build the text branch without IDs, document numbers or the training target."""
    parts = {
        "DESC_RAW": transaction.get("descriptionRaw"),
        "DESC": transaction.get("description"),
        "COUNTERPARTY": _counterparty_name(transaction),
        "MERCHANT": nested_get(transaction, "merchant", "name", default=""),
        "CATEGORY": transaction.get("category"),
        "CNAE": nested_get(transaction, "businessContext", "mainCnae", default=""),
        "ACTIVITY": nested_get(transaction, "businessContext", "businessActivity", default=""),
    }
    return " | ".join(
        f"{key}={normalize_text(value)}" for key, value in parts.items() if normalize_text(value)
    )


def _local_time_features(transaction: Mapping[str, Any]) -> tuple[int, int, bool]:
    derived_hour = nested_get(transaction, "derivedFeatures", "localHour")
    derived_weekday = nested_get(transaction, "derivedFeatures", "localWeekday")
    derived_weekend = nested_get(transaction, "derivedFeatures", "isWeekend")
    if isinstance(derived_hour, int) and isinstance(derived_weekday, int):
        return derived_hour, derived_weekday, bool(derived_weekend)

    raw_date = transaction.get("date")
    if not raw_date:
        return 0, 0, False
    try:
        parsed = datetime.fromisoformat(str(raw_date).replace("Z", "+00:00"))
        timezone_name = str(transaction.get("timezone") or "UTC")
        try:
            parsed = parsed.astimezone(ZoneInfo(timezone_name))
        except ZoneInfoNotFoundError:
            parsed = parsed.astimezone(ZoneInfo("UTC"))
        return parsed.hour, parsed.weekday(), parsed.weekday() >= 5
    except (TypeError, ValueError):
        return 0, 0, False


def _amount_bucket(amount: float) -> str:
    if amount < 10:
        return "LT_10"
    if amount < 50:
        return "10_49"
    if amount < 200:
        return "50_199"
    if amount < 1_000:
        return "200_999"
    if amount < 5_000:
        return "1000_4999"
    return "GE_5000"


def structured_features(transaction: Mapping[str, Any]) -> dict[str, float | str]:
    amount = abs(float(transaction.get("amount", 0.0)))
    direction = str(transaction.get("type") or ("CREDIT" if transaction.get("amount", 0) >= 0 else "DEBIT")).upper()
    payment_method = str(nested_get(transaction, "paymentData", "paymentMethod", default="UNKNOWN"))
    cnae = str(nested_get(transaction, "businessContext", "mainCnae", default="UNKNOWN"))
    category = str(transaction.get("category") or "UNKNOWN")
    operation = str(transaction.get("operationType") or "UNKNOWN")
    counterparty_type = _counterparty_document_type(transaction)
    local_hour, local_weekday, is_weekend = _local_time_features(transaction)
    raw_description = normalize_text(transaction.get("descriptionRaw") or transaction.get("description"))

    return {
        "amount_abs": amount,
        "amount_log1p": math.log1p(amount),
        "amount_bucket": _amount_bucket(amount),
        "amount_is_integer": float(amount.is_integer()),
        "amount_is_round_10": float(amount >= 10 and math.isclose(amount % 10, 0.0, abs_tol=1e-9)),
        "direction": direction,
        "currency": str(transaction.get("currencyCode") or "UNKNOWN"),
        "bank_category": category,
        "operation_type": operation,
        "payment_method": payment_method,
        "provider_code": str(transaction.get("providerCode") or "UNKNOWN"),
        "counterparty_document_type": counterparty_type,
        "company_type": str(nested_get(transaction, "businessContext", "companyType", default="UNKNOWN")),
        "main_cnae": cnae,
        "cnae_category": f"{cnae}|{category}",
        "cnae_operation": f"{cnae}|{operation}",
        "local_hour": float(local_hour),
        "local_weekday": float(local_weekday),
        "is_weekend": float(is_weekend),
        "receiver_present": float(nested_get(transaction, "paymentData", "receiver") is not None),
        "merchant_present": float(transaction.get("merchant") is not None),
        "description_length": float(len(raw_description)),
        "description_digit_count": float(sum(char.isdigit() for char in raw_description)),
        "history_count_30d": float(
            nested_get(transaction, "derivedFeatures", "counterpartyTransactions30d", default=0) or 0
        ),
        "history_count_90d": float(
            nested_get(transaction, "derivedFeatures", "counterpartyTransactions90d", default=0) or 0
        ),
        "same_amount_count_90d": float(
            nested_get(transaction, "derivedFeatures", "sameAmountOccurrences90d", default=0) or 0
        ),
        "amount_ratio_to_median_90d": float(
            nested_get(transaction, "derivedFeatures", "amountRatioToMedian90d", default=1.0) or 1.0
        ),
        "recurrence_type": str(
            nested_get(transaction, "derivedFeatures", "recurrenceType", default="UNKNOWN") or "UNKNOWN"
        ),
    }


class TextFeatureExtractor(TransformerMixin, BaseEstimator):
    """Convert transaction dictionaries into one normalized text per transaction."""

    def fit(self, X: Sequence[Mapping[str, Any]], y: Any = None) -> "TextFeatureExtractor":
        return self

    def transform(self, X: Sequence[Mapping[str, Any]]) -> list[str]:
        return [compose_text(transaction) for transaction in X]


class StructuredFeatureExtractor(TransformerMixin, BaseEstimator):
    """Convert transaction dictionaries into DictVectorizer-compatible features."""

    def fit(self, X: Sequence[Mapping[str, Any]], y: Any = None) -> "StructuredFeatureExtractor":
        return self

    def transform(self, X: Sequence[Mapping[str, Any]]) -> list[dict[str, float | str]]:
        return [structured_features(transaction) for transaction in X]

