# HASS_Aviant

Home Assistant integration for **Inventer Aviant** bathroom fans.

The fans are connected via Bluetooth Low Energy, either through a local Bluetooth
adapter or through [ESPHome Bluetooth proxies](https://esphome.io/components/bluetooth_proxy.html).

## Requirements

- Home Assistant with the `bluetooth` integration set up
- A Bluetooth adapter or an ESPHome BLE proxy within range of the fan

## Installation via HACS

1. Open HACS → ⋮ → **Custom repositories**
2. Add `https://github.com/00joshi/HASS_Aviant` with type **Integration**
3. Install **Inventer Aviant** and restart Home Assistant

## Manual installation

Copy the folder `custom_components/aviant` into the `custom_components` directory
of your Home Assistant configuration and restart Home Assistant.

## Setup

After the restart, the fan is discovered automatically via Bluetooth
(local name `Aviant`). Confirm it under **Settings → Devices & services**.
If it does not show up, add **Inventer Aviant** manually via **Add integration**.

## Issues

Please report problems at https://github.com/00joshi/HASS_Aviant/issues.
