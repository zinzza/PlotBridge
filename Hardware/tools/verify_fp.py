# -*- coding: utf-8 -*-
"""Cross-check: symbol pin number -> signal name  vs  footprint pad number -> physical position.
Ground truth = the board pinout the user confirmed physically (power on the RIGHT, top view)."""
import os, collections
from verify_net import tokenize, parse, val, find_all, find_one   # reuse parser

HW = r"C:\Projects\Arduino\PlotBridge\Hardware"

# ---- ground truth, top view, USB-C at top (-Y). Confirmed against the physical board.
TRUTH = {
  "ESP32-C3_SuperMini": {
    "right": ["5V", "GND", "3V3", "GPIO4", "GPIO3", "GPIO2", "GPIO1", "GPIO0"],
    "left":  ["GPIO5", "GPIO6", "GPIO7", "GPIO8", "GPIO9", "GPIO10", "GPIO20", "GPIO21"],
  },
  # single-row modules: order as printed on the module, pin 1 first
  "ST7789_169_8P":     {"single": ["GND", "VCC", "SCL", "SDA", "RES", "DC", "CS", "BLK"]},
  "MAX3232_MODULE_4P": {"single": ["VCC", "GND", "RX", "TX"]},
}

# ---- symbol: number -> name
sym_map = {}
lib = parse(tokenize(open(os.path.join(HW, "PlotBridge.kicad_sym"), encoding="utf-8").read()))[0]
for sym in find_all(lib, "symbol"):
    name = val(sym[1]).split(":")[-1]
    m = {}
    for sub in find_all(sym, "symbol"):
        for p in find_all(sub, "pin"):
            m[val(find_one(p, "number")[1])] = val(find_one(p, "name")[1])
    if m:
        sym_map[name] = m

# ---- footprint: number -> (x, y)
fp_map = {}
for fn in sorted(os.listdir(os.path.join(HW, "PlotBridge.pretty"))):
    fp = parse(tokenize(open(os.path.join(HW, "PlotBridge.pretty", fn), encoding="utf-8").read()))[0]
    name = val(fp[1])
    pads = {}
    for pad in find_all(fp, "pad"):
        at = find_one(pad, "at")
        pads[val(pad[1])] = (float(val(at[1])), float(val(at[2])))
    fp_map[name] = pads

problems = []
for part, truth in TRUTH.items():
    print("=" * 66)
    print(part)
    print("=" * 66)
    s, f = sym_map[part], fp_map[part]
    if set(s) != set(f):
        problems.append("%s: symbol pins %s != footprint pads %s"
                        % (part, sorted(set(s) - set(f)), sorted(set(f) - set(s))))
        continue
    cols = collections.defaultdict(list)
    for num, (x, y) in f.items():
        cols[x].append((y, num))
    if "single" in truth:
        want = {min(cols): truth["single"]}
    else:
        want = {max(cols): truth["right"], min(cols): truth["left"]}
    for x, order in want.items():
        got = [num for _, num in sorted(cols[x])]          # top -> bottom
        print("  x=%+7.2f  top->bottom" % x)
        for i, num in enumerate(got):
            sig, exp = s[num], order[i] if i < len(order) else "??"
            ok = sig == exp
            print("     pad %-3s  symbol=%-7s expected=%-7s %s" % (num, sig, exp, "ok" if ok else "MISMATCH"))
            if not ok:
                problems.append("%s pad %s: symbol says %s, board says %s" % (part, num, sig, exp))
    print()

print("=" * 66)
if problems:
    print("PROBLEMS (%d):" % len(problems))
    for p in problems:
        print("   -", p)
else:
    print("RESULT: symbol pin numbers and footprint pad positions agree with the physical board")
