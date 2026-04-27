"""Sensor platform for WHOOP."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory, PERCENTAGE, UnitOfEnergy, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import WhoopDataUpdateCoordinator


@dataclass(frozen=True, kw_only=True)
class WhoopSensorDescription(SensorEntityDescription):
    """Describes WHOOP sensor entity."""

    value_key: str


SENSORS: tuple[WhoopSensorDescription, ...] = (
    WhoopSensorDescription(
        key="recovery_score",
        name="Recovery",
        icon="mdi:heart-pulse",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_key="recovery_score",
    ),
    WhoopSensorDescription(
        key="strain",
        name="Strain",
        icon="mdi:arm-flex",
        state_class=SensorStateClass.MEASUREMENT,
        value_key="strain",
    ),
    WhoopSensorDescription(
        key="sleep_performance",
        name="Sleep Performance",
        icon="mdi:sleep",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_key="sleep_performance",
    ),
    WhoopSensorDescription(
        key="resting_heart_rate",
        name="Resting Heart Rate",
        icon="mdi:heart",
        native_unit_of_measurement="bpm",
        device_class=SensorDeviceClass.HEART_RATE,
        state_class=SensorStateClass.MEASUREMENT,
        value_key="resting_heart_rate",
    ),
    WhoopSensorDescription(
        key="heart_rate_variability",
        name="HRV",
        icon="mdi:heart-cog",
        native_unit_of_measurement="ms",
        state_class=SensorStateClass.MEASUREMENT,
        value_key="heart_rate_variability",
    ),
    WhoopSensorDescription(
        key="kilojoule",
        name="Energy",
        icon="mdi:lightning-bolt",
        native_unit_of_measurement=UnitOfEnergy.KILOJOULE,
        state_class=SensorStateClass.MEASUREMENT,
        value_key="kilojoule",
    ),
    WhoopSensorDescription(
        key="sleep_efficiency",
        name="Sleep Efficiency",
        icon="mdi:chart-line",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        value_key="sleep_efficiency",
    ),
    WhoopSensorDescription(
        key="total_sleep_need_ms",
        name="Sleep Need",
        icon="mdi:timer-sand",
        native_unit_of_measurement=UnitOfTime.HOURS,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_key="total_sleep_need_ms",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: WhoopDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(WhoopSensor(coordinator, entry, description) for description in SENSORS)


class WhoopSensor(CoordinatorEntity[WhoopDataUpdateCoordinator], SensorEntity):
    """Representation of a WHOOP sensor."""

    entity_description: WhoopSensorDescription

    def __init__(
        self,
        coordinator: WhoopDataUpdateCoordinator,
        entry: ConfigEntry,
        description: WhoopSensorDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.unique_id}_{description.key}"
        self._attr_has_entity_name = True

    @property
    def native_value(self):
        value = self.coordinator.data.get(self.entity_description.value_key)
        if self.entity_description.value_key == "total_sleep_need_ms" and value is not None:
            return round(float(value) / 3600000, 2)
        return value

    @property
    def extra_state_attributes(self):
        if self.entity_description.key == "sleep_performance":
            return {
                "sleep_start": self.coordinator.data.get("sleep_start"),
                "sleep_end": self.coordinator.data.get("sleep_end"),
            }
        return None
