"""Config-Flow: automatische Bluetooth-Erkennung + manuelle Auswahl."""
from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant.components.bluetooth import (
    BluetoothServiceInfoBleak, async_discovered_service_info)
from homeassistant.config_entries import ConfigEntry, ConfigFlow, OptionsFlow
from homeassistant.const import CONF_ADDRESS, CONF_NAME
from homeassistant.core import callback

from .const import CONF_INTERVAL, DEFAULT_INTERVAL, DOMAIN


class AviantConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    def __init__(self) -> None:
        self._disc: BluetoothServiceInfoBleak | None = None

    async def async_step_bluetooth(self, info: BluetoothServiceInfoBleak):
        await self.async_set_unique_id(info.address)
        self._abort_if_unique_id_configured()
        self._disc = info
        self.context["title_placeholders"] = {"address": info.address}
        return await self.async_step_confirm()

    async def async_step_confirm(self, user_input=None):
        assert self._disc
        if user_input is not None:
            return self._create(self._disc.address, user_input.get(CONF_NAME))
        return self.async_show_form(
            step_id="confirm",
            data_schema=vol.Schema({vol.Optional(CONF_NAME, default=f"Aviant {self._disc.address[-5:]}"): str}),
            description_placeholders={"address": self._disc.address})

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        if user_input is not None:
            await self.async_set_unique_id(user_input[CONF_ADDRESS])
            self._abort_if_unique_id_configured()
            return self._create(user_input[CONF_ADDRESS], user_input.get(CONF_NAME))
        known = self._async_current_ids()
        found = {i.address: f"{i.name} ({i.address}, RSSI {i.rssi})"
                 for i in async_discovered_service_info(self.hass, connectable=True)
                 if i.name == "Aviant" and i.address not in known}
        if not found:
            return self.async_abort(reason="no_devices_found")
        return self.async_show_form(step_id="user", data_schema=vol.Schema({
            vol.Required(CONF_ADDRESS): vol.In(found),
            vol.Optional(CONF_NAME): str}))

    def _create(self, address: str, name: str | None):
        return self.async_create_entry(title=name or f"Aviant {address[-5:]}",
                                       data={CONF_ADDRESS: address})

    @staticmethod
    @callback
    def async_get_options_flow(entry: ConfigEntry) -> OptionsFlow:
        return AviantOptionsFlow()


class AviantOptionsFlow(OptionsFlow):
    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(data=user_input)
        cur = self.config_entry.options.get(CONF_INTERVAL, DEFAULT_INTERVAL)
        return self.async_show_form(step_id="init", data_schema=vol.Schema({
            vol.Required(CONF_INTERVAL, default=cur): vol.All(int, vol.Range(min=30, max=3600))}))
