"""Tests for extract_cost.py — fast mode pricing support."""

import json
import tempfile
from pathlib import Path

import pytest

from src.extract_cost import PRICING, calc_cost, model_key, parse_session


class TestFastModePricing:
    """Fast mode uses flat $30/$150 per Mtok with no cache discount."""

    def test_pricing_exists(self) -> None:
        assert "claude-opus-4-6-fast" in PRICING

    def test_input_price(self) -> None:
        assert PRICING["claude-opus-4-6-fast"]["input"] == 30.00

    def test_output_price(self) -> None:
        assert PRICING["claude-opus-4-6-fast"]["output"] == 150.00

    def test_cache_read_equals_input(self) -> None:
        """Flat pricing means no cache discount."""
        assert PRICING["claude-opus-4-6-fast"]["cache_read"] == 30.00

    def test_cache_create_equals_input(self) -> None:
        """Flat pricing means no cache discount."""
        assert PRICING["claude-opus-4-6-fast"]["cache_create"] == 30.00


class TestModelKeyFastMode:
    """model_key() should resolve fast-mode model strings."""

    def test_exact_key(self) -> None:
        assert model_key("claude-opus-4-6-fast") == "claude-opus-4-6-fast"

    def test_fuzzy_fast_opus(self) -> None:
        assert model_key("claude-opus-4-6-fast-20260301") == "claude-opus-4-6-fast"

    def test_non_fast_opus_unchanged(self) -> None:
        """Regular opus should NOT match fast."""
        assert model_key("claude-opus-4-6") == "claude-opus-4-6"


class TestCalcCostFastMode:
    """calc_cost should use fast mode pricing when model is fast."""

    def test_cost_1m_input_tokens(self) -> None:
        usage = {"input_tokens": 1_000_000, "output_tokens": 0}
        cost = calc_cost("claude-opus-4-6-fast", usage)
        assert cost == pytest.approx(30.00)

    def test_cost_1m_output_tokens(self) -> None:
        usage = {"input_tokens": 0, "output_tokens": 1_000_000}
        cost = calc_cost("claude-opus-4-6-fast", usage)
        assert cost == pytest.approx(150.00)

    def test_cost_cache_read_no_discount(self) -> None:
        usage = {"input_tokens": 0, "output_tokens": 0, "cache_read_input_tokens": 1_000_000}
        cost = calc_cost("claude-opus-4-6-fast", usage)
        assert cost == pytest.approx(30.00)

    def test_cost_cache_create_no_discount(self) -> None:
        usage = {"input_tokens": 0, "output_tokens": 0, "cache_creation_input_tokens": 1_000_000}
        cost = calc_cost("claude-opus-4-6-fast", usage)
        assert cost == pytest.approx(30.00)


class TestParseSessionModelsShape:
    """parse_session models dict must include cost_usd and mirror token totals."""

    def _make_jsonl(self, lines: list[dict]) -> Path:
        tmp = tempfile.NamedTemporaryFile(
            suffix=".jsonl", mode="w", delete=False, encoding="utf-8"
        )
        for line in lines:
            tmp.write(json.dumps(line) + "\n")
        tmp.close()
        return Path(tmp.name)

    def test_models_dict_has_cost_usd(self) -> None:
        """Each model entry in the output must carry a cost_usd field."""
        record = {
            "type": "assistant",
            "timestamp": "2026-01-01T00:00:00Z",
            "message": {
                "model": "claude-opus-4-6",
                "usage": {
                    "input_tokens": 1_000_000,
                    "output_tokens": 0,
                    "cache_read_input_tokens": 0,
                    "cache_creation_input_tokens": 0,
                },
            },
        }
        path = self._make_jsonl([record])
        result = parse_session(path)

        assert "models" in result
        model_entry = result["models"]["claude-opus-4-6"]
        assert "cost_usd" in model_entry
        # 1M input tokens at default pricing should produce a positive cost
        assert model_entry["cost_usd"] > 0
        # token totals should be preserved alongside cost_usd
        assert model_entry["input_tokens"] == 1_000_000
