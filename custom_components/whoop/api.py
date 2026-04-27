"""WHOOP API client."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from aiohttp import ClientSession

from .const import API_BASE_URL


class WhoopApiError(Exception):
    """WHOOP API error."""


@dataclass(slots=True)
class WhoopApiClient:
    """Minimal WHOOP API client for Home Assistant."""

    session: ClientSession
    token: str
    user_id: str

    async def _get(self, endpoint: str) -> dict[str, Any]:
        url = f"{API_BASE_URL}/{endpoint}"
        headers = {"Authorization": f"Bearer {self.token}"}

        async with self.session.get(url, headers=headers, timeout=30) as response:
            if response.status >= 400:
                body = await response.text()
                raise WhoopApiError(
                    f"WHOOP API request failed ({response.status}) for {url}: {body}"
                )

            return await response.json()

    async def async_get_user_id(self) -> str:
        """Resolve WHOOP user_id from token if possible."""
        profile_endpoints = (
            "user/profile/basic",
            "user",
        )

        for endpoint in profile_endpoints:
            try:
                payload = await self._get(endpoint)
            except WhoopApiError:
                continue

            user = payload.get("user") if isinstance(payload.get("user"), dict) else payload
            candidate = (
                user.get("id")
                or user.get("user_id")
                or payload.get("id")
                or payload.get("user_id")
            )
            if candidate is not None and str(candidate).isdigit():
                return str(candidate)

        raise WhoopApiError("Could not resolve WHOOP user_id from token")

    async def async_get_metrics(self) -> dict[str, Any]:
        """Fetch key WHOOP metrics for a user."""
        recovery = await self._get(f"cycle/{self.user_id}?limit=1")
        sleep = await self._get(f"activity/sleep/{self.user_id}?limit=1")

        cycle_record = (recovery.get("records") or [{}])[0]
        sleep_record = (sleep.get("records") or [{}])[0]

        score = cycle_record.get("score") or {}
        sleep_score = sleep_record.get("score") or {}
        stage_summary = sleep_record.get("sleep_needed") or {}

        return {
            "recovery_score": score.get("recovery_score"),
            "strain": score.get("strain"),
            "kilojoule": score.get("kilojoule"),
            "average_heart_rate": cycle_record.get("average_heart_rate"),
            "max_heart_rate": cycle_record.get("max_heart_rate"),
            "resting_heart_rate": cycle_record.get("resting_heart_rate"),
            "heart_rate_variability": cycle_record.get("heart_rate_variability"),
            "sleep_performance": sleep_score.get("sleep_performance_percentage"),
            "sleep_consistency": sleep_score.get("sleep_consistency_percentage"),
            "sleep_efficiency": sleep_score.get("sleep_efficiency_percentage"),
            "total_sleep_need_ms": stage_summary.get("need_from_sleep_debt_milli"),
            "sleep_start": sleep_record.get("start"),
            "sleep_end": sleep_record.get("end"),
        }
