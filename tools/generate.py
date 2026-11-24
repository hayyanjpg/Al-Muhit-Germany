# -*- coding: utf-8 -*-
"""Generator mod 'Al-Muhit Germany' (mod terpisah dari Al-Muhit).

Isi:
  - 200 tech dari mod Al-Muhit (sumber: save 1941.12.1) dipakai Jerman.
  - 24 state GER tahun 1936: manpower x5, resource menurut target nasional.
  - 5 state pesisir dijadikan megalopolis dan masing-masing +8 civilian
    factory (= +40 civilian dari awal). Dockyard tetap 10 seperti vanilla.
  - Tanpa override map/ (tidak ada risiko 'Failed to load the map').

Usage:  python tools/generate.py
"""
import os
import re

GAME = r"D:\SteamLibrary\steamapps\common\Hearts of Iron IV"
MOD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE_MOD = os.path.join(os.path.dirname(MOD), "Al-Muhit")

MANPOWER_MULTIPLIER = 5
RESOURCE_KEYS = ("steel", "tungsten", "rubber", "chromium", "coal",
                 "aluminium", "oil")

# Total resource nasional yang diminta. Rubber tidak disebut, jadi 0.
RESOURCE_TOTALS = {
    "steel": 900,
    "coal": 530,
    "tungsten": 240,
    "chromium": 320,
    "oil": 130,
    "aluminium": 430,
    "rubber": 180,
}

# State yang di-owner GER pada 1 Januari 1936 (dari history vanilla).
GER_STATES = [
    "42-Rhineland.txt",
    "5-Germany.txt",
    "50-Baden.txt",
    "51-Moselland.txt",
    "52-Wuttemberg.txt",
    "53-Oberbayern.txt",
    "54-Bayreuth.txt",
    "55-Nassau.txt",
    "56-Weser-Ems.txt",
    "57-Westfalen.txt",
    "58-Schleswig - Holstein.txt",
    "59-Ost - Hannover.txt",
    "60-Sud-Hannover.txt",
    "61-Mecklenburg.txt",
    "62-Pommern.txt",
    "63-WestPrussen.txt",
    "64-Brandenburg.txt",
    "65-Sachsen.txt",
    "66-Niederschlesien.txt",
    "67-Oberschlesien.txt",
    "68-Wartheland.txt",
    "763-Konigsberg.txt",
    "909-South Schleswig.txt",
    "978 - Actual Baden.txt",
]

# Lima state pesisir yang di-upgrade jadi megalopolis (12 slot dasar,
# jadi 14 setelah bonus industri dari 200 tech).
MEGA_STATES = [
    "56-Weser-Ems.txt",
    "58-Schleswig - Holstein.txt",
    "59-Ost - Hannover.txt",
    "63-WestPrussen.txt",
    "763-Konigsberg.txt",
]
EXTRA_CIVILIAN_PER_STATE = 8  # 5 x 8 = 40 civilian factory tambahan


def w(rel, text):
    path = os.path.join(MOD, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    return path


def cleanup():
    state_dir = os.path.join(MOD, "history", "states")
    if os.path.isdir(state_dir):
        for fn in os.listdir(state_dir):
            if fn.endswith(".txt"):
                os.remove(os.path.join(state_dir, fn))
    hist = os.path.join(MOD, "history", "countries", "GER - Germany.txt")
    if os.path.isfile(hist):
        os.remove(hist)


def read_tech_block():
    """Salin blok set_technology dari mod Al-Muhit (sumber 200 tech)."""
    path = os.path.join(SOURCE_MOD, "history", "countries", "EGY - Egypt.txt")
    if not os.path.isfile(path):
        raise RuntimeError("Al-Muhit tidak ditemukan: %s" % path)
    with open(path, encoding="utf-8-sig", errors="replace") as f:
        txt = f.read()
    m = re.search(r"set_technology\s*=\s*\{.*?\n\}", txt, re.S)
    if m is None:
        raise RuntimeError("blok set_technology tidak ada di %s" % path)
    return m.group(0)


def multiply_manpower(txt, fn):
    def repl(m):
        return m.group(1) + str(int(m.group(2)) * MANPOWER_MULTIPLIER)

    txt, n = re.subn(r"(manpower[ \t]*=[ \t]*)(\d+)", repl, txt, count=1)
    if n == 0:
        raise RuntimeError("baris manpower hilang di %s" % fn)
    return txt


def build_resource_plans():
    """Bagi total resource baru secara proporsional ke pola vanilla.

    Sisa pembulatan dikasih ke state dengan nilai vanilla terbesar supaya
    total nasional persis sama dengan RESOURCE_TOTALS.
    """
    vanilla = {}
    for fn in GER_STATES:
        path = os.path.join(GAME, "history", "states", fn)
        with open(path, encoding="utf-8-sig", errors="replace") as f:
            txt = f.read()
        found = {}
        rr = re.search(r"resources\s*=\s*\{([^}]*)\}", txt, re.S)
        if rr:
            for k in RESOURCE_KEYS:
                m = re.search(r"\b%s\s*=\s*(\d+)" % k, rr.group(1))
                if m:
                    found[k] = int(m.group(1))
        vanilla[fn] = found

    plans = {fn: {} for fn in GER_STATES}
    for key, target in RESOURCE_TOTALS.items():
        current = {fn: vanilla[fn].get(key, 0) for fn in GER_STATES}
        total = sum(current.values())
        if total == 0:
            # Resource yang tidak ada di vanilla (rubber): bagi rata ke
            # semua state GER, sisa pembulatan ke state awal.
            if target:
                base = target // len(GER_STATES)
                remainder = target - base * len(GER_STATES)
                for i, fn in enumerate(GER_STATES):
                    plans[fn][key] = base + (1 if i < remainder else 0)
            continue
        out = {fn: int(v * target / total) for fn, v in current.items()}
        remainder = target - sum(out.values())
        if remainder:
            biggest = max(current, key=current.get)
            out[biggest] += remainder
        for fn, val in out.items():
            plans[fn][key] = val
    return plans


def apply_resources(txt, plan):
    keys = "|".join(RESOURCE_KEYS)
    txt = re.sub(r"\b(%s)[ \t]*=[ \t]*\d+" % keys,
                 lambda m: "%s = %d" % (m.group(1), plan.get(m.group(1), 0)),
                 txt)

    def add_missing(m):
        body = m.group(2)
        for k, v in plan.items():
            if v > 0 and re.search(r"\b%s\s*=" % k, body) is None:
                body += "\t\t%s = %d\n" % (k, v)
        return m.group(1) + body + m.group(3)

    txt, n = re.subn(r"(resources\s*=\s*\{)([^}]*)(\})", add_missing, txt,
                     count=1)
    if n == 0:
        positive = {k: v for k, v in plan.items() if v > 0}
        if positive:
            block = ("\tresources = {\n"
                     + "".join("\t\t%s = %d\n" % (k, v)
                               for k, v in positive.items())
                     + "\t}\n")
            txt, k = re.subn(r"(state_category\s*=\s*\w+[^\n]*\n)",
                             lambda m: m.group(1) + block, txt, count=1)
            if k == 0:
                raise RuntimeError("state_category hilang saat tambah resource")
    return txt


def add_civilian(txt, fn, extra):
    """Tambah `extra` civilian factory ke semua blok buildings (termasuk dated)."""
    txt, n = re.subn(r"(industrial_complex[ \t]*=[ \t]*)(\d+)",
                     lambda m: m.group(1) + str(int(m.group(2)) + extra),
                     txt)
    if n == 0:
        ins = "\t\t\tindustrial_complex = %d\n" % extra
        txt, k = re.subn(r"(buildings\s*=\s*\{\r?\n)",
                         lambda m: m.group(1) + ins, txt, count=1)
        if k == 0:
            raise RuntimeError("blok buildings hilang di %s" % fn)
    return txt


def write_states(plans):
    src = os.path.join(GAME, "history", "states")
    for fn in GER_STATES:
        with open(os.path.join(src, fn), encoding="utf-8-sig",
                  errors="replace") as f:
            txt = f.read()

        txt = multiply_manpower(txt, fn)
        txt = apply_resources(txt, plans[fn])

        tag = "manpower x5, resource sesuai target"
        if fn in MEGA_STATES:
            txt, n = re.subn(r"state_category\s*=\s*\w+",
                             "state_category = megalopolis", txt, count=1)
            if n == 0:
                raise RuntimeError("state_category hilang di %s" % fn)
            txt = add_civilian(txt, fn, EXTRA_CIVILIAN_PER_STATE)
            tag += ", megalopolis, +%d civilian" % EXTRA_CIVILIAN_PER_STATE

        txt = "# Al-Muhit Germany: %s\n" % tag + txt
        w("history/states/" + fn, txt)
    return len(GER_STATES)


def write_country_history():
    src = os.path.join(GAME, "history", "countries", "GER - Germany.txt")
    with open(src, encoding="utf-8-sig", errors="replace") as f:
        txt = f.read()
    tech = read_tech_block()
    marker = r"(capital\s*=\s*\d+[^\n]*\n)"
    txt, n = re.subn(marker,
                     lambda m: m.group(1) + "\n" + tech + "\n",
                     txt, count=1)
    if n == 0:
        raise RuntimeError("baris capital tidak ditemukan di history GER")
    txt = ("# Al-Muhit Germany: 200 tech dari mod Al-Muhit (save 1941.12.1)\n"
           + txt)
    w("history/countries/GER - Germany.txt", txt)


def write_descriptor():
    txt = ('name="Al-Muhit: German Arsenal"\n'
           'version="1.20.0.0"\n'
           'supported_version="1.20.*"\n'
           'path="mod/Al-Muhit Germany"\n')
    w("descriptor.mod", txt)
    w("Al-Muhit Germany.mod", txt)  # salinan di repo biar mudah dibagikan
    parent = os.path.join(os.path.dirname(MOD), "Al-Muhit Germany.mod")
    with open(parent, "w", encoding="utf-8", newline="\n") as f:
        f.write(txt)


def write_readme():
    txt = """# Al-Muhit: German Arsenal

Mod HOI4 1.20.x, **terpisah** dari mod `Al-Muhit`. Tidak ada override `map/`.

## Isi mod
- 200 tech dari mod Al-Muhit (hasil ekstraksi save 1941.12.1) dipakai Jerman
  sejak 1936. Kecepatan riset dan slot riset tetap seperti vanilla.
- 24 state yang di-owner GER pada 1936: manpower **x5** (327.569.535 total).
- Resource nasional GER di-set ke target: steel 900, coal 530, tungsten 240,
  chromium 320, oil 130, aluminium 430, rubber 180. Distribusi per state
  mengikuti pola resource vanilla, dengan sisa pembulatan ke state terbesar.
- 5 state pesisir jadi **megalopolis**: Weser-Ems, Schleswig-Holstein,
  Ost-Hannover, WestPrussen, Konigsberg.
- **+40 civilian factory dari awal**, dibagi rata 8 per state di kelima
  state itu (termasuk blok `1939.1.1`). Dockyard sengaja tidak ditambah:
  total awal tetap 10 seperti vanilla.
- OOB, pemimpin, warna, bendera, dan fokus Jerman tetap vanilla.

## Cara pakai
1. `python tools/generate.py`
2. Aktifkan mod **Al-Muhit: German Arsenal** di launcher (berdampingan dengan
   Al-Muhit juga boleh, keduanya beda folder dan beda tag).
3. Mainkan scenario 1936 sebagai Jerman.
"""
    w("README.md", txt)


def main():
    cleanup()
    plans = build_resource_plans()
    n = write_states(plans)
    write_country_history()
    write_descriptor()
    write_readme()
    mp = sum(int(re.search(r"manpower\s*=\s*(\d+)",
                           open(os.path.join(MOD, "history", "states", fn),
                                encoding="utf-8-sig", errors="replace").read()
                           ).group(1)) for fn in GER_STATES)
    print("OK: %d state GER, manpower x5 = %d" % (n, mp))
    print("RESOURCE   : %s" % ", ".join("%s %d" % (k, v)
                                       for k, v in RESOURCE_TOTALS.items()))
    print("MEGALOPOLIS: %d state, +%d civilian/state = +%d civilian" %
          (len(MEGA_STATES), EXTRA_CIVILIAN_PER_STATE,
           len(MEGA_STATES) * EXTRA_CIVILIAN_PER_STATE))
    print("DOCKYARD   : 10 (vanilla, tanpa bonus)")
    print("TECH       : 200 tech disalin dari mod Al-Muhit")
    print("MOD:", MOD)


if __name__ == "__main__":
    main()
