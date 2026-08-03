# -*- coding: utf-8 -*-
"""Enumerate every track-vs-track crossing on the board and classify it.

Same layer + different net + touching  -> SHORT CIRCUIT (must be zero)
Different layer                        -> harmless, that is what 2 layers are for
"""
import collections, itertools

PCB = r"C:\Projects\Arduino\PlotBridge\Hardware\PlotBridge.kicad_pcb"
CLEARANCE = 0.2      # mm, board rule
TRACK_W   = 0.25     # mm

def tokenize(s):
    out, i, n = [], 0, len(s)
    while i < n:
        c = s[i]
        if c in '()': out.append(c); i += 1
        elif c == '"':
            j = i + 1; buf = []
            while s[j] != '"':
                if s[j] == '\\': buf.append(s[j + 1]); j += 2
                else: buf.append(s[j]); j += 1
            out.append(('STR', ''.join(buf))); i = j + 1
        elif c.isspace(): i += 1
        else:
            j = i
            while j < n and not s[j].isspace() and s[j] not in '()"': j += 1
            out.append(('SYM', s[i:j])); i = j
    return out

def parse(tokens):
    stack = [[]]
    for t in tokens:
        if t == '(': new = []; stack[-1].append(new); stack.append(new)
        elif t == ')': stack.pop()
        else: stack[-1].append(t)
    return stack[0]

val = lambda x: x[1] if isinstance(x, tuple) else x
find_all = lambda n, t: [c for c in n if isinstance(c, list) and c and val(c[0]) == t]
def find_one(n, t):
    r = find_all(n, t); return r[0] if r else None

root = parse(tokenize(open(PCB, encoding='utf-8').read()))[0]
declared = {int(val(n[1])): val(n[2]) for n in find_all(root, 'net')}

segs = []
for s in find_all(root, 'segment'):
    st, en = find_one(s, 'start'), find_one(s, 'end')
    tok = val(find_one(s, 'net')[1])
    net = declared[int(tok)] if tok.lstrip('-').isdigit() else tok
    segs.append((val(find_one(s, 'layer')[1]), net,
                 (float(val(st[1])), float(val(st[2]))),
                 (float(val(en[1])), float(val(en[2])))))

print("tracks: %d   (%s)" % (len(segs), ", ".join(
    "%s=%d" % (l, c) for l, c in collections.Counter(s[0] for s in segs).items())))

# ---- geometry: minimum distance between two segments
def dist_pt_seg(p, a, b):
    px, py = p; ax, ay = a; bx, by = b
    dx, dy = bx - ax, by - ay
    if dx == 0 and dy == 0: return ((px-ax)**2 + (py-ay)**2) ** .5
    t = max(0.0, min(1.0, ((px-ax)*dx + (py-ay)*dy) / (dx*dx + dy*dy)))
    cx, cy = ax + t*dx, ay + t*dy
    return ((px-cx)**2 + (py-cy)**2) ** .5

def segs_intersect(a, b, c, d):
    o = lambda p, q, r: (q[0]-p[0])*(r[1]-p[1]) - (q[1]-p[1])*(r[0]-p[0])
    d1, d2, d3, d4 = o(c,d,a), o(c,d,b), o(a,b,c), o(a,b,d)
    return ((d1 > 0) != (d2 > 0)) and ((d3 > 0) != (d4 > 0))

def seg_gap(s1, s2):
    _, _, a, b = s1
    _, _, c, d = s2
    if segs_intersect(a, b, c, d): return 0.0
    return min(dist_pt_seg(a, c, d), dist_pt_seg(b, c, d),
               dist_pt_seg(c, a, b), dist_pt_seg(d, a, b))

need = CLEARANCE + TRACK_W          # centre-to-centre distance required
same_net_touch = cross_layer = 0
shorts, tight = [], []

for s1, s2 in itertools.combinations(segs, 2):
    lay1, net1 = s1[0], s1[1]
    lay2, net2 = s2[0], s2[1]
    gap = seg_gap(s1, s2)
    if lay1 != lay2:
        if gap == 0.0: cross_layer += 1
        continue
    if net1 == net2:
        if gap < need: same_net_touch += 1
        continue
    if gap == 0.0:
        shorts.append((net1, net2, s1, s2))
    elif gap < need:
        tight.append((net1, net2, round(gap - TRACK_W, 3), s1, s2))

print()
print("cross-layer crossings (F.Cu over B.Cu) : %3d  <- harmless, separated by 1.6mm FR4"
      % cross_layer)
print("same-layer, same-net contacts          : %3d  <- intended (corners / branches)"
      % same_net_touch)
print("same-layer, DIFFERENT-net crossings    : %3d  <- must be 0" % len(shorts))
print("same-layer, DIFFERENT-net under %.2fmm : %3d  <- must be 0" % (CLEARANCE, len(tight)))

for n1, n2, s1, s2 in shorts:
    print("  !! SHORT %s / %s on %s: %s-%s vs %s-%s" % (n1, n2, s1[0], s1[2], s1[3], s2[2], s2[3]))
for n1, n2, g, s1, s2 in tight:
    print("  !! TIGHT %s / %s on %s: edge gap %.3fmm" % (n1, n2, s1[0], g))

print()
if not shorts and not tight:
    print("RESULT: no two different nets touch on the same layer. The red/blue")
    print("        overlaps in the plot are top-over-bottom crossings only.")
else:
    print("RESULT: %d PROBLEMS" % (len(shorts) + len(tight)))
