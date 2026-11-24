# -*- coding: utf-8 -*-
"""Validator statis mod Al-Muhit Germany."""
import os
import re
import sys

MOD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARENT = os.path.dirname(MOD)

MANPOWER_EXPECT = {
    "42-Rhineland.txt": 30277390,
    "5-Germany.txt": 12381080,
    "50-Baden.txt": 30768540,
    "51-Moselland.txt": 61447430,
    "52-Wuttemberg.txt": 26794130,
    "53-Oberbayern.txt": 14533650,
    "54-Bayreuth.txt": 25081590,
    "55-Nassau.txt": 37982350,
    "56-Weser-Ems.txt": 20584670,
    "57-Westfalen.txt": 51093330,
    "58-Schleswig - Holstein.txt": 30956300,
    "59-Ost - Hannover.txt": 24382860,
    "60-Sud-Hannover.txt": 30052140,
    "61-Mecklenburg.txt": 8363530,
    "62-Pommern.txt": 10062210,
    "63-WestPrussen.txt": 11244170,
    "64-Brandenburg.txt": 72650290,
    "65-Sachsen.txt": 55925760,
    "66-Niederschlesien.txt": 30527260,
    "67-Oberschlesien.txt": 14025910,
    "68-Wartheland.txt": 12508400,
    "763-Konigsberg.txt": 21402340,
    "909-South Schleswig.txt": 1525200,
    "978 - Actual Baden.txt": 20568540,
}

RESOURCE_EXPECT = {
    "42-Rhineland.txt": {"steel": 284, "rubber": 8, "coal": 50, "aluminium": 69},
    "5-Germany.txt": {"rubber": 8},
    "50-Baden.txt": {"rubber": 8, "aluminium": 29},
    "51-Moselland.txt": {"steel": 196, "rubber": 8, "coal": 219},
    "52-Wuttemberg.txt": {"rubber": 8, "aluminium": 92},
    "53-Oberbayern.txt": {"rubber": 8},
    "54-Bayreuth.txt": {"rubber": 8, "coal": 28},
    "55-Nassau.txt": {"rubber": 8, "coal": 28},
    "56-Weser-Ems.txt": {"rubber": 8},
    "57-Westfalen.txt": {"rubber": 8},
    "58-Schleswig - Holstein.txt": {"rubber": 8},
    "59-Ost - Hannover.txt": {"rubber": 8, "oil": 130},
    "60-Sud-Hannover.txt": {"steel": 50, "tungsten": 240, "rubber": 7,
                            "chromium": 320, "coal": 28},
    "61-Mecklenburg.txt": {"rubber": 7},
    "62-Pommern.txt": {"rubber": 7},
    "63-WestPrussen.txt": {"steel": 39, "rubber": 7, "aluminium": 29},
    "64-Brandenburg.txt": {"rubber": 7},
    "65-Sachsen.txt": {"steel": 230, "rubber": 7, "coal": 46},
    "66-Niederschlesien.txt": {"steel": 56, "rubber": 7, "coal": 42,
                               "aluminium": 79},
    "67-Oberschlesien.txt": {"steel": 45, "rubber": 7, "coal": 89,
                             "aluminium": 29},
    "68-Wartheland.txt": {"rubber": 7, "aluminium": 74},
    "763-Konigsberg.txt": {"rubber": 7},
    "909-South Schleswig.txt": {"rubber": 7},
    "978 - Actual Baden.txt": {"rubber": 7, "aluminium": 29},
}

# Dockyard hasil +6 per state (urutan mengikuti blok di file).
DOCK_EXPECT = {
    "56-Weser-Ems.txt": [8, 9],
    "58-Schleswig - Holstein.txt": [12, 13],
    "59-Ost - Hannover.txt": [8, 9],
    "63-WestPrussen.txt": [6],
    "763-Konigsberg.txt": [6],
}
MEGA_STATES = list(DOCK_EXPECT)
RESOURCE_TOTALS = {
    "steel": 900, "tungsten": 240, "rubber": 180, "chromium": 320,
    "coal": 530, "aluminium": 430, "oil": 130,
}

errors = []


def check(cond, msg):
    if not cond:
        errors.append(msg)


# --- state ---
resource_sum = {k: 0 for k in RESOURCE_TOTALS}
for fn, mp_expect in MANPOWER_EXPECT.items():
    p = os.path.join(MOD, "history", "states", fn)
    check(os.path.isfile(p), "state hilang: %s" % fn)
    if not os.path.isfile(p):
        continue
    txt = open(p, encoding="utf-8-sig", errors="replace").read()

    m = re.search(r"manpower\s*=\s*(\d+)", txt)
    check(m is not None, "%s: baris manpower hilang" % fn)
    if m:
        check(int(m.group(1)) == mp_expect,
              "%s: manpower %d (harap %d)" % (fn, int(m.group(1)), mp_expect))

    got_res = {}
    rr = re.search(r"resources\s*=\s*\{([^}]*)\}", txt, re.S)
    if rr:
        for k in RESOURCE_TOTALS:
            x = re.search(r"\b%s\s*=\s*(\d+)" % k, rr.group(1))
            if x:
                got_res[k] = int(x.group(1))
                resource_sum[k] += int(x.group(1))
    check(got_res == RESOURCE_EXPECT[fn],
          "%s: resource %s (harap %s)" %
          (fn, got_res, RESOURCE_EXPECT[fn]))

    if fn in MEGA_STATES:
        check(re.search(r"state_category\s*=\s*megalopolis", txt) is not None,
              "%s: bukan megalopolis" % fn)
        got_dock = [int(x) for x in re.findall(r"dockyard\s*=\s*(\d+)", txt)]
        check(got_dock == DOCK_EXPECT[fn],
              "%s: dockyard %s (harap %s)" %
              (fn, got_dock, DOCK_EXPECT[fn]))

for k, v in RESOURCE_TOTALS.items():
    check(resource_sum[k] == v,
          "total %s = %d (harap %d)" % (k, resource_sum[k], v))

dock_start = sum(DOCK_EXPECT[fn][0] for fn in MEGA_STATES)
check(dock_start == 40, "dockyard awal di 5 mega state = %d (harap 40)" % dock_start)
check(dock_start - 10 == 30,
      "dockyard tambahan = %d (harap 30)" % (dock_start - 10))

# --- country history: 200 tech dari Al-Muhit ---
hist = os.path.join(MOD, "history", "countries", "GER - Germany.txt")
check(os.path.isfile(hist), "history country GER hilang")
if os.path.isfile(hist):
    t = open(hist, encoding="utf-8-sig", errors="replace").read()
    check("capital = 64" in t, "capital Jerman bukan 64")
    check("set_grand_doctrine = new_mobile_warfare" in t,
          "grand doctrine vanilla Jerman hilang")
    m = re.search(r"set_technology\s*=\s*\{(.*?)\n\}", t, re.S)
    check(m is not None, "blok set_technology hilang")
    if m:
        techs = re.findall(r"(?m)^\t([a-z0-9_]+) = (\d+)[ \t]*$", m.group(1))
        check(len(techs) == 200,
              "jumlah tech = %d (harap 200)" % len(techs))
        check(dict(techs).get("mechanised_infantry2") == "2",
              "mechanised_infantry2 harus level 2 seperti save Al-Muhit")
# --- tidak ada override peta ---
mapdir = os.path.join(MOD, "map")
check(not os.path.isdir(mapdir) or not os.listdir(mapdir),
      "mod tidak boleh meng-override map/")

# --- descriptor ---
for p in (os.path.join(MOD, "descriptor.mod"),
          os.path.join(PARENT, "Al-Muhit Germany.mod")):
    check(os.path.isfile(p), "descriptor hilang: %s" % p)
    if os.path.isfile(p):
        t = open(p, encoding="utf-8-sig", errors="replace").read()
        check('version="1.20.0.0"' in t, "versi descriptor salah: %s" % p)
        check('supported_version="1.20.*"' in t,
              "supported_version salah: %s" % p)
        check('path="mod/Al-Muhit Germany"' in t,
              "path descriptor salah: %s" % p)

if errors:
    print("VALIDASI GAGAL:")
    for e in errors:
        print(" -", e)
    sys.exit(1)
print("VALIDASI OK: 24 state GER (manpower x10, resource sesuai target), "
      "5 megalopolis +30 dockyard, 200 tech Al-Muhit, tanpa override map/.")
