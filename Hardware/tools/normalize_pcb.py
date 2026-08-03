# -*- coding: utf-8 -*-
"""Post-process the generated board with KiCad's own engine.

Every footprint is reloaded fresh from PlotBridge.pretty and re-placed at the
same position/orientation with the same reference, value and pad nets. That
makes the board's embedded copy identical to the library copy by construction
(hand-written copies drift once a footprint is rotated - KiCad stores footprint
text angle in absolute board coordinates - and DRC then reports
lib_footprint_mismatch).

Run with KiCad's bundled python:
    "C:\\Program Files\\KiCad\\10.0\\bin\\python.exe" normalize_pcb.py
"""
import pcbnew

HW  = r"C:\Projects\Arduino\PlotBridge\Hardware"
PCB = HW + r"\PlotBridge.kicad_pcb"
LIB = HW + r"\PlotBridge.pretty"
mm  = lambda v: v / 1000000.0

bd = pcbnew.LoadBoard(PCB)

n, report = 0, []
for old in list(bd.GetFootprints()):
    ref, val = old.GetReference(), old.GetValue()
    pos, rot = old.GetPosition(), old.GetOrientation()
    name = old.GetFPIDAsString().split(":")[-1]
    # keep net NAMES, not codes - codes are board-scoped and only valid once
    # the new footprint has actually been added to the board
    nets = {p.GetNumber(): p.GetNetname() for p in old.Pads()}

    new = pcbnew.FootprintLoad(LIB, name)
    if new is None:
        raise SystemExit("could not load %s from %s" % (name, LIB))
    new.SetFPID(pcbnew.LIB_ID("PlotBridge", name))
    new.SetReference(ref)
    new.SetValue(val)
    new.SetPosition(pos)
    new.SetOrientation(rot)
    bd.Remove(old)
    bd.Add(new)                       # must be on the board before SetNet
    for p in new.Pads():
        nm = nets.get(p.GetNumber())
        if nm:
            net = bd.FindNet(nm)
            if net is None:
                raise SystemExit("net %r vanished while re-placing %s" % (nm, ref))
            p.SetNet(net)
    n += 1
    report.append("%-3s %-24s (%6.2f, %6.2f) rot=%3.0f  %s"
                  % (ref, new.GetFPIDAsString(), mm(pos.x), mm(pos.y),
                     new.GetOrientationDegrees(),
                     " ".join("%s=%s" % (q.GetNumber(), q.GetNetname())
                              for q in sorted(new.Pads(), key=lambda z: z.GetNumber())
                              if q.GetNetname())))

bd.Save(PCB)
print("reloaded %d footprints from the library and re-saved\n" % n)
print("\n".join(sorted(report)))
