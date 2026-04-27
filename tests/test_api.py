"""Unit tests for WHOOP API parsing helpers."""

from __future__ import annotations

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import AsyncMock, patch

ROOT = Path(__file__).resolve().parents[1]


def load_api_module():
    """Load custom_components.whoop.api without importing Home Assistant."""
    aiohttp_module = types.ModuleType("aiohttp")

    class _ClientSession:  # pragma: no cover - test shim
        pass

    aiohttp_module.ClientSession = _ClientSession
    sys.modules.setdefault("aiohttp", aiohttp_module)

    pkg_custom = types.ModuleType("custom_components")
    pkg_custom.__path__ = [str(ROOT / "custom_components")]
    sys.modules.setdefault("custom_components", pkg_custom)

    pkg_whoop = types.ModuleType("custom_components.whoop")
    pkg_whoop.__path__ = [str(ROOT / "custom_components" / "whoop")]
    sys.modules["custom_components.whoop"] = pkg_whoop

    const_spec = spec_from_file_location(
        "custom_components.whoop.const", ROOT / "custom_components" / "whoop" / "const.py"
    )
    const_module = module_from_spec(const_spec)
    assert const_spec and const_spec.loader
    sys.modules["custom_components.whoop.const"] = const_module
    const_spec.loader.exec_module(const_module)

    api_spec = spec_from_file_location(
        "custom_components.whoop.api", ROOT / "custom_components" / "whoop" / "api.py"
    )
    api_module = module_from_spec(api_spec)
    assert api_spec and api_spec.loader
    sys.modules["custom_components.whoop.api"] = api_module
    api_spec.loader.exec_module(api_module)
    return api_module


api_module = load_api_module()
WhoopApiClient = api_module.WhoopApiClient
WhoopApiError = api_module.WhoopApiError


class TestWhoopApiClient(unittest.IsolatedAsyncioTestCase):
    """Test WHOOP API client parsing behavior."""

    async def test_resolves_user_id_from_user_object(self) -> None:
        client = WhoopApiClient(session=AsyncMock(), token="t", user_id="")

        with patch.object(WhoopApiClient, "_get", new=AsyncMock(return_value={"user": {"id": 10129}})):
            user_id = await client.async_get_user_id()

        self.assertEqual(user_id, "10129")

    async def test_resolves_user_id_from_root_field(self) -> None:
        client = WhoopApiClient(session=AsyncMock(), token="t", user_id="")

        with patch.object(WhoopApiClient, "_get", new=AsyncMock(return_value={"user_id": 55555})):
            user_id = await client.async_get_user_id()

        self.assertEqual(user_id, "55555")

    async def test_raises_when_user_id_cannot_be_resolved(self) -> None:
        client = WhoopApiClient(session=AsyncMock(), token="t", user_id="")

        with patch.object(WhoopApiClient, "_get", new=AsyncMock(return_value={"foo": "bar"})):
            with self.assertRaises(WhoopApiError):
                await client.async_get_user_id()

    async def test_maps_metrics_payload(self) -> None:
        client = WhoopApiClient(session=AsyncMock(), token="t", user_id="123")

        async def fake_get(_self, endpoint: str):
            if endpoint.startswith("cycle/"):
                return {
                    "records": [
                        {
                            "average_heart_rate": 70,
                            "max_heart_rate": 155,
                            "resting_heart_rate": 53,
                            "heart_rate_variability": 95,
                            "score": {
                                "recovery_score": 82,
                                "strain": 12.7,
                                "kilojoule": 9500,
                            },
                        }
                    ]
                }
            return {
                "records": [
                    {
                        "start": "2026-04-26T22:30:00Z",
                        "end": "2026-04-27T06:20:00Z",
                        "score": {
                            "sleep_performance_percentage": 87,
                            "sleep_consistency_percentage": 78,
                            "sleep_efficiency_percentage": 92,
                        },
                        "sleep_needed": {
                            "need_from_sleep_debt_milli": 28800000,
                        },
                    }
                ]
            }

        with patch.object(WhoopApiClient, "_get", new=fake_get):
            data = await client.async_get_metrics()

        self.assertEqual(data["recovery_score"], 82)
        self.assertEqual(data["strain"], 12.7)
        self.assertEqual(data["sleep_performance"], 87)
        self.assertEqual(data["sleep_efficiency"], 92)
        self.assertEqual(data["resting_heart_rate"], 53)


if __name__ == "__main__":
    unittest.main()
