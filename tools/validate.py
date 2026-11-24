# -*- coding: utf-8 -*-
"""Validator statis mod Al-Muhit Germany."""
import os
import re
import sys

MOD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARENT = os.path.dirname(MOD)

MANPOWER_EXPECT = {
    "42-Rhineland.txt": 15138695,
    "5-Germany.txt": 6190540,
    "50-Baden.txt": 15384270,
    "51-Moselland.txt": 30723715,
    "52-Wuttemberg.txt": 13397065,
    "53-Oberbayern.txt": 7266825,
    "54-Bayreuth.txt": 12540795,
    "55-Nassau.txt": 18991175,
    "56-Weser-Ems.txt": 10292335,
    "57-Westfalen.txt": 25546665,
    "58-Schleswig - Holstein.txt": 15478150,
    "59-Ost - Hannover.txt": 12191430,
    "60-Sud-Hannover.txt": 15026070,
    "61-Mecklenburg.txt": 4181765,
    "62-Pommern.txt": 5031105,
    "63-WestPrussen.txt": 5622085,
    "64-Brandenburg.txt": 36325145,
    "65-Sachsen.txt": 27962880,
    "66-Niederschlesien.txt": 15263630,
    "67-Oberschlesien.txt": 7012955,
    "68-Wartheland.txt": 6254200,
    "763-Konigsberg.txt": 10701170,
    "909-South Schleswig.txt": 762600,
    "978 - Actual Baden.txt": 10284270,
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

# Dockyard sengaja sama dengan vanilla (total awal 10).
DOCK_EXPECT = {
    "56-Weser-Ems.txt": [2, 3],
    "58-Schleswig - Holstein.txt": [6, 7],
    "59-Ost - Hannover.txt": [2, 3],
    "63-WestPrussen.txt": [],
    "763-Konigsberg.txt": [],
}

# Civilian = nilai vanilla + 8 per mega state (urutan mengikuti blok di file).
CIV_EXPECT = {
    "56-Weser-Ems.txt": [10, 12],
    "58-Schleswig - Holstein.txt": [8],
    "59-Ost - Hannover.txt": [9, 13],
    "63-WestPrussen.txt": [9],
    "763-Konigsberg.txt": [10],
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
        got_civ = [int(x) for x in re.findall(r"industrial_complex\s*=\s*(\d+)",
                                              txt)]
        check(got_civ == CIV_EXPECT[fn],
              "%s: civilian %s (harap %s)" %
              (fn, got_civ, CIV_EXPECT[fn]))

for k, v in RESOURCE_TOTALS.items():
    check(resource_sum[k] == v,
          "total %s = %d (harap %d)" % (k, resource_sum[k], v))

dock_start = sum(DOCK_EXPECT[fn][0] if DOCK_EXPECT[fn] else 0
                 for fn in MEGA_STATES)
check(dock_start == 10,
      "dockyard awal di 5 mega state = %d (harap 10)" % dock_start)
VANILLA_START_CIV = {
    "56-Weser-Ems.txt": 2, "58-Schleswig - Holstein.txt": 0,
    "59-Ost - Hannover.txt": 1, "63-WestPrussen.txt": 1,
    "763-Konigsberg.txt": 2,
}
civ_added = sum(CIV_EXPECT[fn][0] - VANILLA_START_CIV[fn]
                for fn in MEGA_STATES)
check(civ_added == 40,
      "civilian tambahan awal = %d (harap 40)" % civ_added)

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
print("VALIDASI OK: 24 state GER (manpower x5, resource sesuai target), "
      "5 megalopolis +40 civilian, dockyard 10, 200 tech Al-Muhit, "
      "tanpa override map/.")
