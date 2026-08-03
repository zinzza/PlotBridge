# -*- coding: utf-8 -*-
"""Check the .kicad_pcb pad->net assignment against the same expectation used for
the schematic. DRC only proves the board is self-consistent; this proves it is RIGHT."""
import collections

PCB = r"C:\Projects\Arduino\PlotBridge\Hardware\PlotBridge.kicad_pcb"

def tokenize(s):
    out, i, n = [], 0, len(s)
    while i < n:
        c = s[i]
        if c in '()':
            out.append(c); i += 1
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
find_all = lambda node, tag: [c for c in node if isinstance(c, list) and c and val(c[0]) == tag]
def find_one(node, tag):
    r = find_all(node, tag)
    return r[0] if r else None

root = parse(tokenize(open(PCB, encoding='utf-8').read()))[0]

declared = {int(val(n[1])): val(n[2]) for n in find_all(root, 'net')}
board = collections.defaultdict(set)
refs = {}
for fp in find_all(root, 'footprint'):
    props = {val(p[1]): val(p[2]) for p in find_all(fp, 'property')}
    ref = props.get('Reference')
    refs[ref] = val(fp[1])
    for pad in find_all(fp, 'pad'):
        nn = find_one(pad, 'net')
        if nn:
            # KiCad writes either (net N "NAME") or, once it has re-saved, (net "NAME")
            name = val(nn[2]) if len(nn) > 2 else val(nn[1])
            board[name].add((ref, val(pad[1])))

# tracks per net (sanity: every routed net must have segments).
# A segment carries either (net N) or, after KiCad re-saves, (net "NAME").
seg = collections.Counter()
for s in find_all(root, 'segment'):
    tok = val(find_one(s, 'net')[1])
    seg[declared[int(tok)] if tok.lstrip('-').isdigit() else tok] += 1

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

print("footprints on board:", ", ".join("%s=%s" % (r, n) for r, n in sorted(refs.items())))
print()
print("%-9s %-6s %-30s %s" % ("NET", "SEGS", "PADS", "RESULT"))
print("-" * 72)
bad = 0
for net, want in sorted(expect.items()):
    have = board.get(net, set())
    ok = have == want
    print("%-9s %-6d %-30s %s" % (net, seg.get(net, 0),
          ",".join("%s.%s" % p for p in sorted(want)), "PASS" if ok else "FAIL got %s" % sorted(have)))
    if not ok: bad += 1
    if seg.get(net, 0) == 0:
        print("        !! net has no track segments"); bad += 1

for net in sorted(set(board) - set(expect)):
    print("!! unexpected net on board:", net, sorted(board[net])); bad += 1

print("-" * 72)
print("RESULT:", "board matches the schematic netlist" if bad == 0 else "%d PROBLEMS" % bad)
