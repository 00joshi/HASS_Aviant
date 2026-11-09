"""BLE-Protokoll Inventer Aviant (reverse engineered, nur lesend)."""
from __future__ import annotations

import struct
from dataclasses import dataclass, field
from typing import Any

_S = "-2f33-11e7-93ae-92361f002671"
SET = {n: f"7c4adc{n:02x}{_S}" for n in (1, 2, 3, 4, 5, 7, 11)}
LIVE = "528b80e8-c47a-4c0a-bdf1-916a7748f412"
NAME = "b85fa07a-9382-4838-871c-81d045dcc2ff"
SW = "00002a28-0000-1000-8000-00805f9b34fb"
HW = "00002a27-0000-1000-8000-00805f9b34fb"
MODEL = "00002a24-0000-1000-8000-00805f9b34fb"

EMPF = {1: "niedrig", 2: "mittel", 3: "hoch"}
RPM_PER_PCT = 24


def _u16(b: bytes, i: int) -> int:
    return struct.unpack_from("<H", b, i)[0]


def _pct(rpm: int) -> int:
    return round(rpm / RPM_PER_PCT)


def _txt(b: bytes | None) -> str | None:
    return b.rstrip(b"\0").decode("utf8", "replace") if b else None


@dataclass
class AviantData:
    name: str | None = None
    sw: str | None = None
    hw: str | None = None
    model: str | None = None
    values: dict[str, Any] = field(default_factory=dict)


def decode(raw: dict[str, bytes | None]) -> AviantData:
    d: dict[str, Any] = {}
    if (b := raw.get(LIVE)) and len(b) >= 14:
        ref = _u16(b, 10)
        rpm = _u16(b, 8)
        d |= {
            "temperatur": b[13],
            "feuchte_roh": _u16(b, 2),
            "voc": _u16(b, 4),
            "voc_referenz": ref,
            "voc_abweichung": round((_u16(b, 4) / ref - 1) * 100) if ref else None,
            "drehzahl": rpm,
            "leistung": _pct(rpm),
            "lueftet": rpm > 0,
            "status_raw": b.hex(),
        }
    if (x := raw.get(SET[1])) and len(x) >= 4:
        d |= {"feuchtesensor": bool(x[0]), "empf_feuchte": EMPF.get(x[1]), "stufe_feuchte": _pct(_u16(x, 2))}
    if (x := raw.get(SET[2])) and len(x) >= 4:
        d |= {"lichtsensor": bool(x[0]), "empf_licht": EMPF.get(x[1]),
              "luftqualitaetssensor": bool(x[2]), "empf_luftqualitaet": EMPF.get(x[3])}
    if (x := raw.get(SET[3])) and len(x) >= 3:
        d |= {"dauermodus": bool(x[0]), "grundlueftung": _pct(_u16(x, 1))}
    if (x := raw.get(SET[4])) and len(x) >= 5:
        d |= {"timer_laufzeit": x[0], "timer": bool(x[1]), "timer_verzoegerung": x[2], "stufe_timer": _pct(_u16(x, 3))}
    if (x := raw.get(SET[5])) and len(x) >= 5:
        d |= {"lueftungsfunktion": bool(x[0]), "lueftung_laufzeit": x[2], "stufe_lueftung": _pct(_u16(x, 3))}
    if (x := raw.get(SET[7])) and len(x) >= 5:
        d |= {"boost": bool(x[0]), "boost_restzeit": _u16(x, 3) if x[0] else 0}
    if (x := raw.get(SET[11])) and len(x) >= 3:
        d |= {"stufe_luftqualitaet": _pct(struct.unpack_from(">H", x, 1)[0])}  # big-endian!
    return AviantData(_txt(raw.get(NAME)), _txt(raw.get(SW)), _txt(raw.get(HW)), _txt(raw.get(MODEL)), d)


async def read_all(client) -> dict[str, bytes | None]:
    """Liest alle relevanten Characteristics über einen verbundenen BleakClient."""
    raw: dict[str, bytes | None] = {}
    for uuid in (LIVE, *SET.values(), NAME, SW, HW, MODEL):
        try:
            raw[uuid] = bytes(await client.read_gatt_char(uuid))
        except Exception:  # noqa: BLE001 – einzelne Fehler tolerieren
            raw[uuid] = None
    return raw
