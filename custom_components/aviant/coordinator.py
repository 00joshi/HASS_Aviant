"""Polling-Coordinator: verbindet sich zyklisch (lokal oder über ESPHome-Proxy)."""
from __future__ import annotations

import logging
from datetime import timedelta

from bleak_retry_connector import BleakClientWithServiceCache, establish_connection
from homeassistant.components import bluetooth
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DOMAIN
from .protocol import AviantData, decode, read_all

_LOGGER = logging.getLogger(__name__)


class AviantCoordinator(DataUpdateCoordinator[AviantData]):
    def __init__(self, hass: HomeAssistant, address: str, interval: int) -> None:
        super().__init__(hass, _LOGGER, name=f"{DOMAIN} {address}",
                         update_interval=timedelta(seconds=interval))
        self.address = address

    async def _async_update_data(self) -> AviantData:
        dev = bluetooth.async_ble_device_from_address(self.hass, self.address, connectable=True)
        if dev is None:
            raise UpdateFailed(f"{self.address} nicht in Reichweite (oder App verbunden)")
        try:
            client = await establish_connection(BleakClientWithServiceCache, dev, self.address,
                                                max_attempts=3)
        except Exception as err:
            raise UpdateFailed(f"Verbindung fehlgeschlagen: {err}") from err
        try:
            raw = await read_all(client)
        finally:
            await client.disconnect()  # sofort trennen, damit die App das Gerät wieder sieht
        data = decode(raw)
        if not data.values:
            raise UpdateFailed("Keine Daten gelesen")
        return data
