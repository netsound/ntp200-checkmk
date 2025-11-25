#!/usr/bin/env python3
"""
Filename: ntp200_piggyback.py
Author: Fred Moses
Date: 2025-11-25
Version: 1.0
Description:
fetch multiple NTP200s JSONS and send piggyback resules to local agent on Checkmk server

Place file in  /usr/lib/check_mk_agent/local/ folder

License: MIT License
Contact: fred@moses.bz
"""
import json
import urllib.request
import urllib.error
import time

# NTP200 endpoints (hostname here must match Checkmk host name in WATO!)
DEVICES = [
    {"name": "ntp-demo3.centerclick",  "url": "http://ntp-demo3.centerclick.com/json"},
#    {"name": "clock2.host", "url": "http://clock2/json"},
#    {"name": "clock3.host",  "url": "http://clock3/json"},
]

TIMEOUT = 5

GPS_MIN_SAT_USED_WARN = 4
GPS_MIN_SAT_USED_CRIT = 1

# Temperature thresholds (SoC)
TEMP_WARN = 130.0     # °C
TEMP_CRIT = 140.0     # °C

NTP_JITTER_WARN = 0.01
NTP_JITTER_CRIT = 0.1

STRATUM_WARN = 3
STRATUM_CRIT = 5


def fetch_json(url: str):
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        raw = resp.read().decode("utf-8", errors="replace")
    return json.loads(raw)

def do_device(dev):
    name = dev["name"]
    url = dev["url"]
    now = int(time.time())

    try:
        data = fetch_json(url)
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, json.JSONDecodeError) as e:
        print(f"<<<<{name}>>>>")
        print(now)
        print("<<<local>>>")
        print(f'2 "ntp200_overall" - CRIT - unable to fetch/parse JSON from {url}: {e}')
        print("<<<<>>>>")
        return

    gps = data.get("gps", {})
    ntp = data.get("ntp", {})
    client = ntp.get("client", {})

    ntp_status = ntp.get("status", "unknown")
    stratum = ntp.get("stratum", None)
    jitter = ntp.get("jitter", None)
    sys_jitter = ntp.get("sys_jitter", None)

    ntp_client_count = client.get("count", None)      # total
    ntp_client_v4 = client.get("v4_count", None)      # ipv4
    ntp_client_v6 = client.get("v6_count", None)      # ipv6

    power = data.get("power", {})
    temp = data.get("temp", {})
    stats = data.get("stats", {})

    hostname = data.get("HOSTNAME", name)
    swver = data.get("SWVER", "?")
    swver_latest = data.get("SWVER_LATEST", "?")

    gps_status = gps.get("status", "unknown")
    sat_used = gps.get("sat_used", 0)
    sat_seen = gps.get("sat_seen", 0)

    ntp_status = ntp.get("status", "unknown")
    stratum = ntp.get("stratum", None)
    jitter = ntp.get("jitter", None)
    sys_jitter = ntp.get("sys_jitter", None)

    dc_volts = power.get("dc", None)
    power_status = power.get("status", "unknown")

    soc_temp = temp.get("soc", None)
    temp_status = temp.get("status", "unknown")

    uptime_sec = data.get("uptime_sec", None)
    runtime = stats.get("runtime", None)

    # ---------------- GPS ----------------
    gps_state = 0
    gps_reasons = []

    if gps_status != "3d-fix":
        gps_state = max(gps_state, 1)
        gps_reasons.append(f"status={gps_status}")
    if sat_used is not None:
        if sat_used <= GPS_MIN_SAT_USED_CRIT:
            gps_state = max(gps_state, 2)
            gps_reasons.append(f"sat_used={sat_used}<= {GPS_MIN_SAT_USED_CRIT}")
        elif sat_used < GPS_MIN_SAT_USED_WARN:
            gps_state = max(gps_state, 1)
            gps_reasons.append(f"sat_used={sat_used}< {GPS_MIN_SAT_USED_WARN}")

    if not gps_reasons:
        gps_reasons.append("OK")

    gps_metrics = []
    if sat_used is not None:
        gps_metrics.append(f"gps_sat_used={sat_used};{GPS_MIN_SAT_USED_WARN};{GPS_MIN_SAT_USED_CRIT};;")
    if sat_seen is not None:
        gps_metrics.append(f"gps_sat_seen={sat_seen};;;;")
    gps_perfdata = "|".join(gps_metrics) if gps_metrics else "-"

    gps_summary = f"{hostname} GPS status={gps_status}, sat_used={sat_used}/{sat_seen} ({'; '.join(gps_reasons)})"

    # ---------------- NTP ----------------
    ntp_state = 0
    ntp_reasons = []

    if ntp_status != "good":
        ntp_state = max(ntp_state, 1)
        ntp_reasons.append(f"status={ntp_status}")

    if stratum is not None:
        if stratum != 1:
            ntp_state = max(ntp_state, 1)
            ntp_reasons.append(f"stratum={stratum}")
        if stratum >= STRATUM_CRIT:
            ntp_state = max(ntp_state, 2)
            ntp_reasons.append(f"stratum>={STRATUM_CRIT}")
        elif stratum >= STRATUM_WARN:
            ntp_state = max(ntp_state, 1)
            ntp_reasons.append(f"stratum>={STRATUM_WARN}")

    if jitter is not None:
        if jitter >= NTP_JITTER_CRIT:
            ntp_state = max(ntp_state, 2)
            ntp_reasons.append(f"jitter={jitter:.6f}s>={NTP_JITTER_CRIT}")
        elif jitter >= NTP_JITTER_WARN:
            ntp_state = max(ntp_state, 1)
            ntp_reasons.append(f"jitter={jitter:.6f}s>={NTP_JITTER_WARN}")

    if not ntp_reasons:
        ntp_reasons.append("OK")

    ntp_metrics = []
    if jitter is not None:
        ntp_metrics.append(f"ntp_jitter={jitter:.6f};{NTP_JITTER_WARN};{NTP_JITTER_CRIT};;")
    if sys_jitter is not None:
        ntp_metrics.append(f"ntp_sys_jitter={sys_jitter:.6f};;;;")
    if stratum is not None:
        ntp_metrics.append(f"ntp_stratum={stratum};{STRATUM_WARN};{STRATUM_CRIT};;")
    ntp_perfdata = "|".join(ntp_metrics) if ntp_metrics else "-"

    ntp_summary = f"{hostname} NTP status={ntp_status}, stratum={stratum}, jitter={jitter} ({'; '.join(ntp_reasons)})"

    # ---------------- ENV ----------------
    env_state = 0
    env_reasons = []

    if power_status != "good":
        env_state = max(env_state, 2)
        env_reasons.append(f"power_status={power_status}")

    if temp_status != "good":
        env_state = max(env_state, 1)
        env_reasons.append(f"temp_status={temp_status}")

    if soc_temp is not None:
        if soc_temp >= TEMP_CRIT:
            env_state = max(env_state, 2)
            env_reasons.append(f"soc_temp={soc_temp:.1f}°C>={TEMP_CRIT}")
        elif soc_temp >= TEMP_WARN:
            env_state = max(env_state, 1)
            env_reasons.append(f"soc_temp={soc_temp:.1f}°C>={TEMP_WARN}")

    if not env_reasons:
        env_reasons.append("OK")

    env_metrics = []
    if dc_volts is not None:
        env_metrics.append(f"dc_volts={dc_volts:.2f};;;;")  # no V suffix
    if soc_temp is not None:
        env_metrics.append(f"soc_temp={soc_temp:.2f};{TEMP_WARN};{TEMP_CRIT};;")
    if uptime_sec is not None:
        env_metrics.append(f"uptime_sec={uptime_sec};;;;")  # no s suffix
    if runtime is not None:
        env_metrics.append(f"runtime_sec={runtime};;;;")
    env_perfdata = "|".join(env_metrics) if env_metrics else "-"

    env_summary = (
        f"{hostname} DC={dc_volts}V ({power_status}), "
        f"SoC={soc_temp}°C ({temp_status}), uptime={uptime_sec}s "
        f"({' ; '.join(env_reasons)})"
    )

    # ---------------- OVERALL ----------------
    overall_state = max(gps_state, ntp_state, env_state)
    overall_reasons = []
    if gps_state:
        overall_reasons.append(f"GPS={gps_state}")
    if ntp_state:
        overall_reasons.append(f"NTP={ntp_state}")
    if env_state:
        overall_reasons.append(f"ENV={env_state}")
    if not overall_reasons:
        overall_reasons.append("OK")

    overall_metrics = []
    overall_metrics.extend(gps_metrics)
    overall_metrics.extend(ntp_metrics)
    overall_metrics.extend(env_metrics)
    overall_perfdata = "|".join(overall_metrics) if overall_metrics else "-"

    overall_summary = (
        f"{hostname} SW={swver} (latest {swver_latest}), "
        f"GPS={gps_status} sat_used={sat_used}/{sat_seen}, "
        f"NTP={ntp_status} stratum={stratum} jitter={jitter}, "
        f"DC={dc_volts}V ({power_status}) SoC={soc_temp}°C ({temp_status}) "
        f"({' ; '.join(overall_reasons)})"
    )

    # ------------- Piggyback block -------------
    print(f"<<<<{name}>>>>")
    print(now)
    print("<<<local>>>")
    print(f'{gps_state} "ntp200_gps" {gps_perfdata} {gps_summary}')
    print(f'{ntp_state} "ntp200_ntp" {ntp_perfdata} {ntp_summary}')
    print(f'{env_state} "ntp200_env" {env_perfdata} {env_summary}')
    print(f'{overall_state} "ntp200_overall" {overall_perfdata} {overall_summary}')
    print("<<<<>>>>")


def main():
    for dev in DEVICES:
        do_device(dev)


if __name__ == "__main__":
    main()

