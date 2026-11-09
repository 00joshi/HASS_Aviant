"""Basis-Entity."""
from __future__ import annotations

from homeassistant.helpers.device_registry import CONNECTION_BLUETOOTH, DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import AviantCoordinator


class AviantEntity(CoordinatorEntity[AviantCoordinator]):
    _attr_has_entity_name = True

    def __init__(self, coord: AviantCoordinator, entry, key: str) -> None:
        super().__init__(coord)
        self._key = key
        self._attr_unique_id = f"{coord.address}_{key}"
        self._attr_translation_key = key
        d = coord.data
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coord.address)},
            connections={(CONNECTION_BLUETOOTH, coord.address)},
            name=entry.title, manufacturer="Inventer",
            model=f"Aviant ({d.model})" if d and d.model else "Aviant",
            sw_version=d.sw if d else None, hw_version=d.hw if d else None,
            suggested_area=d.name if d else None)

    @property
    def _value(self):
        return self.coordinator.data.values.get(self._key) if self.coordinator.data else None

    @property
    def available(self) -> bool:
        return super().available and self._value is not None
