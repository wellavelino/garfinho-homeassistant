"""Sensor exposing how many recipes are favorited."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import GarfinhoCoordinator


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    async_add_entities([FavoritesSensor(entry.runtime_data)])


class FavoritesSensor(CoordinatorEntity[GarfinhoCoordinator], SensorEntity):
    _attr_has_entity_name = True
    _attr_translation_key = "favorites"
    _attr_icon = "mdi:bookmark-multiple"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = "recipes"

    def __init__(self, coordinator: GarfinhoCoordinator) -> None:
        super().__init__(coordinator)
        entry = coordinator.config_entry
        self._attr_unique_id = f"{entry.unique_id}_favorites"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.unique_id or entry.entry_id)},
            name="Garfinho",
            manufacturer="Garfinho (unofficial)",
            entry_type=DeviceEntryType.SERVICE,
        )

    @property
    def native_value(self) -> int:
        return self.coordinator.data.count

    @property
    def extra_state_attributes(self) -> Mapping[str, Any]:
        return {"recipes": self.coordinator.data.titles, "folders": self.coordinator.data.folders}
