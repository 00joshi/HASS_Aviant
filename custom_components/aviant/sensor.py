"""Sensoren."""
from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass, SensorEntity, SensorEntityDescription, SensorStateClass)
from homeassistant.const import PERCENTAGE, REVOLUTIONS_PER_MINUTE, EntityCategory, UnitOfTemperature, UnitOfTime

from .entity import AviantEntity

M, D = SensorStateClass.MEASUREMENT, EntityCategory.DIAGNOSTIC
EMPF_OPTS = ["niedrig", "mittel", "hoch"]
SENSORS = [
    SensorEntityDescription("temperatur", device_class=SensorDeviceClass.TEMPERATURE,
                            native_unit_of_measurement=UnitOfTemperature.CELSIUS, state_class=M),
    SensorEntityDescription("feuchte_roh", icon="mdi:water-percent", state_class=M),
    SensorEntityDescription("voc", icon="mdi:air-filter", state_class=M),
    SensorEntityDescription("voc_referenz", icon="mdi:air-filter", state_class=M, entity_registry_enabled_default=False),
    SensorEntityDescription("voc_abweichung", icon="mdi:delta", native_unit_of_measurement=PERCENTAGE, state_class=M),
    SensorEntityDescription("drehzahl", icon="mdi:fan", native_unit_of_measurement=REVOLUTIONS_PER_MINUTE, state_class=M),
    SensorEntityDescription("leistung", icon="mdi:fan", native_unit_of_measurement=PERCENTAGE, state_class=M),
    SensorEntityDescription("boost_restzeit", device_class=SensorDeviceClass.DURATION,
                            native_unit_of_measurement=UnitOfTime.SECONDS),
    SensorEntityDescription("status_raw", icon="mdi:code-brackets", entity_category=D,
                            entity_registry_enabled_default=False),
    *[SensorEntityDescription(k, icon="mdi:fan-speed-2", native_unit_of_measurement=PERCENTAGE, entity_category=D)
      for k in ("grundlueftung", "stufe_feuchte", "stufe_luftqualitaet", "stufe_lueftung", "stufe_timer")],
    *[SensorEntityDescription(k, icon="mdi:tune", device_class=SensorDeviceClass.ENUM, options=EMPF_OPTS, entity_category=D)
      for k in ("empf_feuchte", "empf_licht", "empf_luftqualitaet")],
    *[SensorEntityDescription(k, icon="mdi:timer-outline", native_unit_of_measurement=UnitOfTime.MINUTES, entity_category=D)
      for k in ("timer_laufzeit", "timer_verzoegerung", "lueftung_laufzeit")],
]


async def async_setup_entry(hass, entry, add):
    add(AviantSensor(entry.runtime_data, entry, d) for d in SENSORS)


class AviantSensor(AviantEntity, SensorEntity):
    def __init__(self, coord, entry, desc: SensorEntityDescription) -> None:
        super().__init__(coord, entry, desc.key)
        self.entity_description = desc

    @property
    def native_value(self):
        return self._value
