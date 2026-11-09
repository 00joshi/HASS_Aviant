"""Binärsensoren."""
from __future__ import annotations

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass, BinarySensorEntity, BinarySensorEntityDescription)
from homeassistant.const import EntityCategory

from .entity import AviantEntity

R, D = BinarySensorDeviceClass.RUNNING, EntityCategory.DIAGNOSTIC
BINARY = [
    BinarySensorEntityDescription("lueftet", device_class=R, icon="mdi:fan"),
    BinarySensorEntityDescription("boost", device_class=R, icon="mdi:rocket-launch"),
    BinarySensorEntityDescription("dauermodus", icon="mdi:fan-clock"),
    *[BinarySensorEntityDescription(k, entity_category=D) for k in
      ("feuchtesensor", "lichtsensor", "luftqualitaetssensor", "lueftungsfunktion", "timer")],
]


async def async_setup_entry(hass, entry, add):
    add(AviantBinary(entry.runtime_data, entry, d) for d in BINARY)


class AviantBinary(AviantEntity, BinarySensorEntity):
    def __init__(self, coord, entry, desc) -> None:
        super().__init__(coord, entry, desc.key)
        self.entity_description = desc

    @property
    def is_on(self):
        return self._value
