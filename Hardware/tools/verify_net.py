# -*- coding: utf-8 -*-
"""Parse the generated .kicad_sch, rebuild KiCad connectivity semantics, print the netlist.

Implements: wire-to-wire endpoints, T-junctions (endpoint lying mid-segment),
pin/label attachment, and NAME-based joining (labels + power symbols).
"""
import collections

SCH = r"C:\Projects\Arduino\PlotBridge\Hardware\PlotBridge.kicad_sch"

# ---------------------------------------------------------------- s-expr parser
def tokenize(s):
    out, i, n = [], 0, len(s)
    while i < n:
        c = s[i]
        if c in '()':
            out.append(c); i += 1
        elif c == '"':
            j = i + 1; buf = []
            while s[j] != '"':
                if s[j] == '\\':
                    buf.append(s[j + 1]); j += 2
                else:
                    buf.append(s[j]); j += 1
            out.append(('STR', ''.join(buf))); i = j + 1
        elif c.isspace():
            i += 1
        else:
            j = i
            while j < n and not s[j].isspace() and s[j] not in '()"':
                j += 1
            out.append(('SYM', s[i:j])); i = j
    return out

def parse(tokens):
    stack = [[]]
    for t in tokens:
        if t == '(':
            new = []; stack[-1].append(new); stack.append(new)
        elif t == ')':
            stack.pop()
        else:
            stack[-1].append(t)
    return stack[0]

val      = lambda x: x[1] if isinstance(x, tuple) else x
find_all = lambda node, tag: [c for c in node if isinstance(c, list) and c and val(c[0]) == tag]
def find_one(node, tag):
    r = find_all(node, tag)
    return r[0] if r else None
P = lambda x, y: (round(float(val(x)), 3), round(float(val(y)), 3))

root = parse(tokenize(open(SCH, encoding='utf-8').read()))[0]

# ---------------------------------------------------------------- lib symbols
libpins = {}
for sym in find_all(find_one(root, 'lib_symbols'), 'symbol'):
    pins = []
    for sub in find_all(sym, 'symbol'):
        for p in find_all(sub, 'pin'):
            at = find_one(p, 'at')
            pins.append((val(find_one(p, 'number')[1]), val(find_one(p, 'name')[1]),
                         float(val(at[1])), float(val(at[2]))))
    libpins[val(sym[1])] = pins

# ---------------------------------------------------------------- placed symbols
Pin = collections.namedtuple('Pin', 'ref num name pt')
placed_pins, powersyms = [], []
for sym in find_all(root, 'symbol'):
    lid_node = find_one(sym, 'lib_id')
    if not lid_node:
        continue
    lid = val(lid_node[1])
    at = find_one(sym, 'at')
    X, Y, rot = float(val(at[1])), float(val(at[2])), float(val(at[3]))
    assert rot == 0, "non-zero rotation not handled"
    props = {val(pr[1]): val(pr[2]) for pr in find_all(sym, 'property')}
    ref, value = props.get('Reference'), props.get('Value')
    assert lid in libpins, "missing lib_symbol: " + lid
    is_pwr = ref.startswith('#PWR')
    label_ref = value if is_pwr else ref
    for num, nm, px, py in libpins[lid]:
        pt = (round(X + px, 3), round(Y - py, 3))
        if is_pwr:
            powersyms.append((value, pt))
        else:
            placed_pins.append(Pin(label_ref, num, nm, pt))

wires = [(P(find_all(find_one(w, 'pts'), 'xy')[0][1], find_all(find_one(w, 'pts'), 'xy')[0][2]),
          P(find_all(find_one(w, 'pts'), 'xy')[1][1], find_all(find_one(w, 'pts'), 'xy')[1][2]))
         for w in find_all(root, 'wire')]
labels = [(val(l[1]), P(find_one(l, 'at')[1], find_one(l, 'at')[2])) for l in find_all(root, 'label')]
ncs    = {P(find_one(c, 'at')[1], find_one(c, 'at')[2]) for c in find_all(root, 'no_connect')}

# ---------------------------------------------------------------- union-find
parent = {}
def find(p):
    parent.setdefault(p, p)
    while parent[p] != p:
        parent[p] = parent[parent[p]]; p = parent[p]
    return p
def union(a, b):
    ra, rb = find(a), find(b)
    if ra != rb: parent[ra] = rb

for a, b in wires:
    union(a, b)

def on_segment(pt, a, b):
    if a == b: return False
    (x, y), (x1, y1), (x2, y2) = pt, a, b
    if abs((x2 - x1) * (y - y1) - (y2 - y1) * (x - x1)) > 1e-6: return False
    return (min(x1, x2) - 1e-6 <= x <= max(x1, x2) + 1e-6
            and min(y1, y2) - 1e-6 <= y <= max(y1, y2) + 1e-6)

# T-junctions: any anchor or wire endpoint touching another wire's body
anchors = ([p.pt for p in placed_pins] + [pt for _, pt in labels]
           + [pt for _, pt in powersyms] + [e for w in wires for e in w])
for pt in anchors:
    for a, b in wires:
        if on_segment(pt, a, b):
            union(pt, a)

# NAME-based connectivity: labels and power symbols join by name, not geometry
for nm, pt in labels:
    union(pt, ('NAME', nm))
for nm, pt in powersyms:
    if nm != 'PWR_FLAG':
        union(pt, ('NAME', nm))
    else:
        union(pt, ('FLAGPT', pt))     # keep it in whatever net it touches

# ---------------------------------------------------------------- nets
groups = collections.defaultdict(list)
for p in placed_pins:
    groups[find(p.pt)].append(p)
names = collections.defaultdict(set)
for nm, pt in labels:
    names[find(pt)].add(nm)
for nm, pt in powersyms:
    if nm != 'PWR_FLAG':
        names[find(pt)].add(nm)
flagged = {find(pt) for nm, pt in powersyms if nm == 'PWR_FLAG'}

print("=" * 72)
print("NETLIST  (rebuilt from geometry + label/power-name joining)")
print("=" * 72)
got, problems = {}, []
for g, pins in sorted(groups.items(), key=lambda kv: sorted(names.get(kv[0], {'~'}))):
    nm = sorted(names.get(g, []))
    if len(nm) > 1:
        problems.append("multiple names shorted together: %s" % nm)
    net = nm[0] if nm else None
    conn = sorted({(p.ref, p.num, p.name) for p in pins})
    if net is None:
        continue
    got[net] = {(r, n) for r, n, _ in conn}
    print("\n%-9s%s" % (net, "   [PWR_FLAG]" if g in flagged else ""))
    for ref, num, pname in conn:
        print("           %-4s pin %-3s %s" % (ref, num, pname))

print("\n" + "=" * 72)
print("PINS WITH NO NET")
print("=" * 72)
named_pts = {find(p.pt) for p in placed_pins if names.get(find(p.pt))}
for p in placed_pins:
    if find(p.pt) not in named_pts:
        ok = p.pt in ncs
        print("   %-4s pin %-3s %-8s  %s" % (p.ref, p.num, p.name,
              "no_connect OK" if ok else "!! FLOATING"))
        if not ok:
            problems.append("floating pin %s.%s (%s)" % (p.ref, p.num, p.name))

# ---------------------------------------------------------------- expectations
expect = {
    '+3V3':    {('U1', '6'), ('U2', '2'), ('U3', '1')},
    'GND':     {('U1', '7'), ('U2', '1'), ('U3', '2')},
    'LCD_CS':  {('U1', '3'),  ('U2', '7')},
    'LCD_DC':  {('U1', '4'),  ('U2', '6')},
    'LCD_SCL': {('U1', '5'),  ('U2', '3')},
    'LCD_SDA': {('U1', '10'), ('U2', '4')},
    'LCD_RST': {('U1', '2'),  ('U2', '5')},
    'LCD_BL':  {('U1', '9'),  ('U2', '8')},
    'UART_TX': {('U1', '1'),  ('U3', '3')},
    'UART_RX': {('U1', '11'), ('U3', '4')},
}
print("\n" + "=" * 72)
print("CHECK vs Docs/pinmap.md")
print("=" * 72)
for net, want in sorted(expect.items()):
    have = got.get(net, set())
    print("%-5s %-9s %s" % ("PASS" if have == want else "FAIL", net, sorted(want)))
    if have != want:
        problems.append("%s: expected %s got %s" % (net, sorted(want), sorted(have)))
for net in sorted(set(got) - set(expect)):
    problems.append("unexpected net: %s" % net)

if not flagged:
    problems.append("PWR_FLAG is not attached to any net (ERC will complain)")

print("\n" + "=" * 72)
if problems:
    print("PROBLEMS (%d):" % len(problems))
    for p in problems:
        print("   -", p)
else:
    print("RESULT: ALL CHECKS PASSED")
