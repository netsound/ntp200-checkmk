#!/usr/bin/env python3
"""
Filename: ntp200_perfometers.py
Author: Fred Moses
Date: 2025-11-25
Version: 1.0
Description:
Perf-O-Meters for NTP200 metrics on Checkmk server

Place file in  /omd/sites/sitename/share/check_mk/web/plugins/perfometer/ folder

License: MIT License
Contact: fred@moses.bz
"""
from cmk.gui.i18n import _
from cmk.gui.plugins.metrics import perfometer_info

# --------- Power / Temperature ---------

# DC volts (e.g. 0–15 V)
perfometer_info.append(
    {
        "type": "linear",
        "title": _("NTP200 DC voltage"),
        "segments": ["dc_volts"],
        "total": 15.0,
    }
)

# SoC temp (0–160 °C; matches your high thresholds)
perfometer_info.append(
    {
        "type": "linear",
        "title": _("NTP200 SoC temperature"),
        "segments": ["soc_temp"],
        "total": 160.0,
    }
)

# --------- GPS ---------

# Satellites used (0–32, tweak if you like)
perfometer_info.append(
    {
        "type": "linear",
        "title": _("NTP200 GPS satellites used"),
        "segments": ["gps_sat_used"],
        "total": 32.0,
    }
)

# --------- NTP ---------

# Jitter (0–0.1 s, since WARN=0.01, CRIT=0.1)
perfometer_info.append(
    {
        "type": "linear",
        "title": _("NTP200 NTP jitter"),
        "segments": ["ntp_jitter"],
        "total": 0.1,
    }
)

# Stratum (0–16, the NTP spec max)
perfometer_info.append(
    {
        "type": "linear",
        "title": _("NTP200 NTP stratum"),
        "segments": ["ntp_stratum"],
        "total": 16.0,
    }
)

# Total clients (adjust total= if you expect more/less)
perfometer_info.append(
    {
        "type": "linear",
        "title": _("NTP200 NTP clients (total)"),
        "segments": ["ntp_client_count"],
        "total": 500.0,   # assume up to ~500; tweak for your environment
    }
)

# (Optional) separate IPv4/IPv6 client bar
perfometer_info.append(
    {
        "type": "stacked",
        "title": _("NTP200 NTP clients v4/v6"),
        "segments": ["ntp_client_v4", "ntp_client_v6"],
        "total": 500.0,
    }
)


# --------- Uptime (optional) ---------

# Uptime bar (0–1,000,000 s ≈ 11.5 days)
perfometer_info.append(
    {
        "type": "linear",
        "title": _("NTP200 uptime"),
        "segments": ["uptime_sec"],
        "total": 1_000_000.0,
    }
)
