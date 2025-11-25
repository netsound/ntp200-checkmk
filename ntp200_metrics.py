#!/usr/bin/env python3
"""
Filename: ntp200_metrics.py
Author: Fred Moses
Date: 2025-11-25
Version: 1.0
Description:
custom metric definitions for NTP200 local checks on Checkmk server

Place file in /omd/sites/sitename/share/check_mk/web/plugins/metrics/ folder

License: MIT License
Contact: fred@moses.bz
"""
from cmk.gui.i18n import _
from cmk.gui.plugins.metrics import metric_info

# ------------- Power / Temperature -------------

# DC voltage metric (from local check field "dc_volts")
metric_info["dc_volts"] = {
    "title": _("DC voltage"),
    "unit": "v",   # volts
    "color": "11/a",
}

# SoC temperature metric (from local check field "soc_temp")
metric_info["soc_temp"] = {
    "title": _("SoC temperature"),
    "unit": "c",   # degrees Celsius
    "color": "21/a",
}

# ------------- GPS -------------

metric_info["gps_sat_used"] = {
    "title": _("GPS satellites used"),
    "unit": "count",
    "color": "41/a",
}

metric_info["gps_sat_seen"] = {
    "title": _("GPS satellites seen"),
    "unit": "count",
    "color": "42/a",
}

# ------------- NTP -------------

metric_info["ntp_jitter"] = {
    "title": _("NTP jitter"),
    "unit": "s",
    "color": "31/a",
}

metric_info["ntp_sys_jitter"] = {
    "title": _("NTP system jitter"),
    "unit": "s",
    "color": "32/a",
}

metric_info["ntp_stratum"] = {
    "title": _("NTP stratum"),
    "unit": "count",
    "color": "33/a",
}

# NEW: NTP client counts

metric_info["ntp_client_count"] = {
    "title": _("NTP clients (total)"),
    "unit": "count",
    "color": "34/a",
}

metric_info["ntp_client_v4"] = {
    "title": _("NTP clients IPv4"),
    "unit": "count",
    "color": "35/a",
}

metric_info["ntp_client_v6"] = {
    "title": _("NTP clients IPv6"),
    "unit": "count",
    "color": "36/a",
}


# ------------- Time / Runtime -------------

metric_info["uptime_sec"] = {
    "title": _("Device uptime"),
    "unit": "s",
    "color": "51/a",
}

metric_info["runtime_sec"] = {
    "title": _("Runtime since last reset"),
    "unit": "s",
    "color": "52/a",
}
