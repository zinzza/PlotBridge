# -*- coding: utf-8 -*-
"""Generate the PlotBridge KiCad project (schematic + symbol/footprint libs + board)."""
import os, json, math, itertools

OUT = r"C:\Projects\Arduino\PlotBridge\Hardware"
PRETTY = os.path.join(OUT, "PlotBridge.pretty")
os.makedirs(PRETTY, exist_ok=True)

_ctr = itertools.count(1)
def U():
    n = next(_ctr)
    return "5e17b1d9-%04x-4a00-8000-%012x" % (n & 0xFFFF, n)

ROOT_UUID = "5e17b1d9-0000-4a00-8000-000000000000"
PROJ = "PlotBridge"
FONT = "(effects (font (size 1.27 1.27)))"
FONT_H = "(effects (font (size 1.27 1.27)) (hide yes))"

# ================================================================ SYMBOLS
ESP_LEFT  = [("1","GPIO0",8.89),("2","GPIO1",6.35),("3","GPIO2",3.81),
             ("4","GPIO3",1.27),("5","GPIO4",-1.27)]
ESP_RIGHT = [("9","GPIO5",8.89),("10","GPIO6",6.35),("11","GPIO7",3.81),
             ("12","GPIO8",1.27),("13","GPIO9",-1.27),("14","GPIO10",-3.81),
             ("15","GPIO20",-6.35),("16","GPIO21",-8.89)]
LCD_PINS  = [("3","SCL",7.62),("4","SDA",5.08),("5","RES",2.54),
             ("6","DC",0.0),("7","CS",-2.54),("8","BLK",-5.08)]

def pin(etype, x, y, ang, length, name, number):
    return ('\t\t\t(pin %s line (at %s %s %s) (length %s)\n'
            '\t\t\t\t(name "%s" %s)\n\t\t\t\t(number "%s" %s)\n\t\t\t)\n'
            % (etype, x, y, ang, length, name, FONT, number, FONT))

def rect(x1, y1, x2, y2):
    return ('\t\t\t(rectangle (start %s %s) (end %s %s)\n'
            '\t\t\t\t(stroke (width 0.254) (type default))\n'
            '\t\t\t\t(fill (type background))\n\t\t\t)\n' % (x1, y1, x2, y2))

def sym_header(name, ref, value, footprint, desc):
    return ('\t(symbol "%s:%s"\n\t\t(pin_names (offset 1.016))\n'
            '\t\t(exclude_from_sim no)\n\t\t(in_bom yes)\n\t\t(on_board yes)\n'
            '\t\t(property "Reference" "%s" (at 0 20.32 0) %s)\n'
            '\t\t(property "Value" "%s" (at 0 17.78 0) %s)\n'
            '\t\t(property "Footprint" "%s" (at 0 0 0) %s)\n'
            '\t\t(property "Datasheet" "" (at 0 0 0) %s)\n'
            '\t\t(property "Description" "%s" (at 0 0 0) %s)\n'
            % (PROJ, name, ref, FONT, value, FONT, footprint, FONT_H, FONT_H, desc, FONT_H))

def sym_esp():
    s = sym_header("ESP32-C3_SuperMini", "U", "ESP32-C3 SuperMini",
                   "PlotBridge:ESP32-C3_SuperMini",
                   "ESP32-C3 SuperMini module, 16-pin 2x8 THT (Tenstar/nologo)")
    s += '\t\t(symbol "ESP32-C3_SuperMini_0_1"\n' + rect(-12.7, 12.7, 12.7, -12.7) + '\t\t)\n'
    s += '\t\t(symbol "ESP32-C3_SuperMini_1_1"\n'
    s += pin("power_in",  -5.08, 15.24, 270, 2.54, "5V",  "8")
    s += pin("power_out",  5.08, 15.24, 270, 2.54, "3V3", "6")
    s += pin("power_in",   0.00,-15.24,  90, 2.54, "GND", "7")
    for num, nm, y in ESP_LEFT:
        s += pin("bidirectional", -15.24, y, 0, 2.54, nm, num)
    for num, nm, y in ESP_RIGHT:
        s += pin("bidirectional", 15.24, y, 180, 2.54, nm, num)
    return s + '\t\t)\n\t)\n'

def sym_lcd():
    s = sym_header("ST7789_169_8P", "U", "ST7789 1.69in 240x280",
                   "PlotBridge:ST7789_169_8P",
                   "1.69in 240x280 ST7789 SPI LCD module, 8-pin header")
    s += '\t\t(symbol "ST7789_169_8P_0_1"\n' + rect(-10.16, 12.7, 10.16, -12.7) + '\t\t)\n'
    s += '\t\t(symbol "ST7789_169_8P_1_1"\n'
    s += pin("power_in", 0.00, 15.24, 270, 2.54, "VCC", "2")
    s += pin("power_in", 0.00,-15.24,  90, 2.54, "GND", "1")
    for num, nm, y in LCD_PINS:
        s += pin("input", -12.7, y, 0, 2.54, nm, num)
    return s + '\t\t)\n\t)\n'

def sym_max():
    s = sym_header("MAX3232_MODULE_4P", "U", "MAX3232 module 4P",
                   "PlotBridge:MAX3232_MODULE_4P",
                   "MAX3232 RS-232 transceiver module, 4-pin TTL side, DB9 on module")
    s += '\t\t(symbol "MAX3232_MODULE_4P_0_1"\n' + rect(-10.16, 7.62, 10.16, -7.62) + '\t\t)\n'
    s += '\t\t(symbol "MAX3232_MODULE_4P_1_1"\n'
    s += pin("power_in", 0.00, 10.16, 270, 2.54, "VCC", "1")
    s += pin("power_in", 0.00,-10.16,  90, 2.54, "GND", "2")
    s += pin("input",   -12.7,  2.54,   0, 2.54, "RX",  "3")
    s += pin("output",  -12.7, -2.54,   0, 2.54, "TX",  "4")
    return s + '\t\t)\n\t)\n'

def poly(pts, fill="none"):
    p = " ".join("(xy %s %s)" % (x, y) for x, y in pts)
    return ('\t\t\t(polyline (pts %s)\n\t\t\t\t(stroke (width 0) (type default))\n'
            '\t\t\t\t(fill (type %s))\n\t\t\t)\n' % (p, fill))

def sym_power(name, graphics, etype):
    s = ('\t(symbol "%s:%s"\n\t\t(power)\n\t\t(pin_numbers hide)\n'
         '\t\t(pin_names (offset 0) hide)\n\t\t(exclude_from_sim no)\n'
         '\t\t(in_bom yes)\n\t\t(on_board yes)\n'
         '\t\t(property "Reference" "#PWR" (at 0 -3.81 0) %s)\n'
         '\t\t(property "Value" "%s" (at 0 3.556 0) %s)\n'
         '\t\t(property "Footprint" "" (at 0 0 0) %s)\n'
         '\t\t(property "Datasheet" "" (at 0 0 0) %s)\n'
         '\t\t(property "Description" "Power symbol" (at 0 0 0) %s)\n'
         % (PROJ, name, FONT_H, name, FONT, FONT_H, FONT_H, FONT_H))
    s += '\t\t(symbol "%s_0_1"\n%s\t\t)\n' % (name, graphics)
    s += '\t\t(symbol "%s_1_1"\n' % name + pin(etype, 0, 0, 90, 0, name, "1")
    return s + '\t\t)\n\t)\n'

G_3V3 = poly([(-0.762,1.27),(0,2.54),(0.762,1.27)]) + poly([(0,0),(0,2.54)])
G_GND = poly([(0,0),(0,-1.27),(1.27,-1.27),(0,-2.54),(-1.27,-1.27),(0,-1.27)])
G_FLG = poly([(0,0),(0,1.27),(-1.016,1.905),(0,2.54),(1.016,1.905),(0,1.27)])

SYMBOLS = (sym_esp() + sym_lcd() + sym_max()
           + sym_power("+3V3", G_3V3, "power_in")
           + sym_power("GND",  G_GND, "power_in")
           + sym_power("PWR_FLAG", G_FLG, "power_out"))

with open(os.path.join(OUT, "PlotBridge.kicad_sym"), "w", encoding="utf-8") as f:
    f.write('(kicad_symbol_lib\n\t(version 20231120)\n\t(generator "kicad_symbol_editor")\n'
            '\t(generator_version "8.0")\n' + SYMBOLS + ')\n')

# ================================================================ SCHEMATIC
W, LB, NC, SY, JN = [], [], [], [], []

def wire(x1, y1, x2, y2):
    W.append('\t(wire (pts (xy %s %s) (xy %s %s))\n\t\t(stroke (width 0) (type default))\n'
             '\t\t(uuid "%s")\n\t)\n' % (x1, y1, x2, y2, U()))

def label(x, y, name, side):
    ang, just = (0, "left") if side == "R" else (180, "right")
    LB.append('\t(label "%s" (at %s %s %s)\n\t\t(effects (font (size 1.27 1.27)) '
              '(justify %s bottom))\n\t\t(uuid "%s")\n\t)\n' % (name, x, y, ang, just, U()))

def noconn(x, y):
    NC.append('\t(no_connect (at %s %s) (uuid "%s"))\n' % (x, y, U()))

def junction(x, y):
    JN.append('\t(junction (at %s %s) (diameter 0) (color 0 0 0 0) (uuid "%s"))\n' % (x, y, U()))

def place(libname, ref, value, footprint, x, y, pins, rx=2.54, ry=-17.78):
    s  = '\t(symbol\n\t\t(lib_id "%s:%s")\n\t\t(at %s %s 0)\n\t\t(unit 1)\n' % (PROJ, libname, x, y)
    s += '\t\t(exclude_from_sim no)\n\t\t(in_bom yes)\n\t\t(on_board yes)\n\t\t(dnp no)\n'
    s += '\t\t(uuid "%s")\n' % U()
    s += '\t\t(property "Reference" "%s" (at %s %s 0) %s)\n' % (ref, x + rx, y + ry, FONT)
    s += '\t\t(property "Value" "%s" (at %s %s 0) %s)\n' % (value, x + rx, y + ry + 2.54, FONT)
    s += '\t\t(property "Footprint" "%s" (at %s %s 0) %s)\n' % (footprint, x, y, FONT_H)
    s += '\t\t(property "Datasheet" "" (at %s %s 0) %s)\n' % (x, y, FONT_H)
    s += '\t\t(property "Description" "" (at %s %s 0) %s)\n' % (x, y, FONT_H)
    for p in pins:
        s += '\t\t(pin "%s" (uuid "%s"))\n' % (p, U())
    s += ('\t\t(instances\n\t\t\t(project "%s"\n\t\t\t\t(path "/%s" (reference "%s") (unit 1))\n'
          '\t\t\t)\n\t\t)\n\t)\n' % (PROJ, ROOT_UUID, ref))
    SY.append(s)

_pwr = itertools.count(1)
def place_pwr(libname, value, x, y):
    place(libname, "#PWR%02d" % next(_pwr), value, "", x, y, ["1"], rx=2.54, ry=-1.27)

UX, UY = 88.9, 100.33
place("ESP32-C3_SuperMini", "U1", "ESP32-C3 SuperMini",
      "PlotBridge:ESP32-C3_SuperMini", UX, UY, [str(i) for i in range(1, 17)], ry=-20.32)

NET_L = {"1": "UART_TX", "2": "LCD_RST", "3": "LCD_CS", "4": "LCD_DC", "5": "LCD_SCL"}
for num, nm, ly in ESP_LEFT:
    py = UY - ly
    wire(UX - 15.24, py, UX - 25.4, py); label(UX - 25.4, py, NET_L[num], "L")

NET_R = {"9": "LCD_BL", "10": "LCD_SDA", "11": "UART_RX"}
for num, nm, ly in ESP_RIGHT:
    py = UY - ly
    if num in NET_R:
        wire(UX + 15.24, py, UX + 25.4, py); label(UX + 25.4, py, NET_R[num], "R")
    else:
        noconn(UX + 15.24, py)

noconn(UX - 5.08, UY - 15.24)
wire(UX + 5.08, UY - 15.24, UX + 5.08, UY - 20.32)
place_pwr("+3V3", "+3V3", UX + 5.08, UY - 20.32)
wire(UX, UY + 15.24, UX, UY + 20.32)
place_pwr("GND", "GND", UX, UY + 20.32)
junction(UX, UY + 17.78)
wire(UX, UY + 17.78, UX + 12.7, UY + 17.78)
place_pwr("PWR_FLAG", "PWR_FLAG", UX + 12.7, UY + 17.78)

LX, LY = 172.72, 100.33
place("ST7789_169_8P", "U2", "ST7789 1.69in 240x280",
      "PlotBridge:ST7789_169_8P", LX, LY, [str(i) for i in range(1, 9)], ry=-20.32)
LCD_NET = {"3": "LCD_SCL", "4": "LCD_SDA", "5": "LCD_RST",
           "6": "LCD_DC", "7": "LCD_CS", "8": "LCD_BL"}
for num, nm, ly in LCD_PINS:
    py = LY - ly
    wire(LX - 12.7, py, LX - 22.86, py); label(LX - 22.86, py, LCD_NET[num], "L")
wire(LX, LY - 15.24, LX, LY - 20.32); place_pwr("+3V3", "+3V3", LX, LY - 20.32)
wire(LX, LY + 15.24, LX, LY + 20.32); place_pwr("GND", "GND", LX, LY + 20.32)

MX, MY = 172.72, 149.86
place("MAX3232_MODULE_4P", "U3", "MAX3232 module 4P",
      "PlotBridge:MAX3232_MODULE_4P", MX, MY, ["1", "2", "3", "4"], ry=-15.24)
for num, nm, ly, net in [("3", "RX", 2.54, "UART_TX"), ("4", "TX", -2.54, "UART_RX")]:
    py = MY - ly
    wire(MX - 12.7, py, MX - 22.86, py); label(MX - 22.86, py, net, "L")
wire(MX, MY - 10.16, MX, MY - 15.24); place_pwr("+3V3", "+3V3", MX, MY - 15.24)
wire(MX, MY + 10.16, MX, MY + 15.24); place_pwr("GND", "GND", MX, MY + 15.24)

TEXTS = [
    (20.32, 25.4,  "PlotBridge - WiFi(TCP 9100) to RS-232 bridge for HPGL plotters"),
    (20.32, 30.48, "UART: 9600-8-N-1, no flow control.  GPIO0=TX -> MAX3232 RX,  GPIO7=RX <- MAX3232 TX"),
    (20.32, 35.56, "GPIO8 = onboard LED (LOW=ON), GPIO9 = onboard BOOT button (10s long-press = WiFi reset)"),
    (20.32, 175.26,"NOTE: verify the MAX3232 module supports 3.3V VCC before connecting power."),
    (20.32, 180.34,"NOTE: RS-232 is on the module's own DB9. Cross-connect: MAX3232 TX -> plotter RX, RX <- plotter TX."),
]
TX = "".join('\t(text "%s" (at %s %s 0)\n\t\t(effects (font (size 1.27 1.27)) (justify left bottom))\n'
             '\t\t(uuid "%s")\n\t)\n' % (t, x, y, U()) for x, y, t in TEXTS)

sch = ('(kicad_sch\n\t(version 20231120)\n\t(generator "eeschema")\n\t(generator_version "8.0")\n'
       '\t(uuid "%s")\n\t(paper "A4")\n\t(title_block\n\t\t(title "PlotBridge")\n'
       '\t\t(date "2026-07-28")\n\t\t(rev "A")\n\t)\n\t(lib_symbols\n%s\t)\n' % (ROOT_UUID, SYMBOLS))
sch += "".join(JN) + "".join(W) + "".join(NC) + "".join(LB) + TX + "".join(SY)
sch += '\t(sheet_instances\n\t\t(path "/" (page "1"))\n\t)\n)\n'
with open(os.path.join(OUT, "PlotBridge.kicad_sch"), "w", encoding="utf-8") as f:
    f.write(sch)

# ================================================================ FOOTPRINTS
# One body generator, used for BOTH the .kicad_mod and the board copy, so the
# board never drifts from the library (avoids DRC lib_footprint_mismatch).
def L1(x1, y1, x2, y2, layer="F.SilkS", w=0.12):
    return ('\t(fp_line (start %s %s) (end %s %s)\n\t\t(stroke (width %s) (type solid))\n'
            '\t\t(layer "%s")\n\t\t(uuid "%s")\n\t)\n' % (x1, y1, x2, y2, w, layer, U()))

def prop1(key, value, y, layer, rot=0):
    # fp text angle is board-absolute, so a rotated footprint needs it applied
    # here too, otherwise DRC flags lib_footprint_mismatch against the library.
    return ('\t(property "%s" "%s" (at 0 %s %s)\n\t\t(layer "%s")\n\t\t(uuid "%s")\n'
            '\t\t(effects (font (size 1 1) (thickness 0.15)))\n\t)\n'
            % (key, value, y, rot, layer, U()))

def fp_body(part, refname, valname, nets=None, rot=0):
    silk, pads, extra, reflayer, drill = (part[k] for k in
                                          ("silk", "pads", "extra", "reflayer", "drill"))
    b  = prop1("Reference", refname, part.get("refy", silk[1] - 1.5), reflayer, rot)
    b += prop1("Value", valname, silk[3] + 1.5, "F.Fab", rot)
    if silk[0] is not None:
        b += (L1(silk[0], silk[1], silk[2], silk[1]) + L1(silk[2], silk[1], silk[2], silk[3])
              + L1(silk[2], silk[3], silk[0], silk[3]) + L1(silk[0], silk[3], silk[0], silk[1]))
    b += extra()
    for num, x, y in pads:
        if drill == "np":
            b += ('\t(pad "" np_thru_hole circle (at %s %s) (size 3.2 3.2) (drill 3.2)\n'
                  '\t\t(layers "F&B.Cu" "*.Mask")\n\t\t(uuid "%s")\n\t)\n' % (x, y, U()))
        else:
            nt = '\t\t(net %d "%s")\n' % nets[num] if (nets and num in nets) else ""
            b += ('\t(pad "%s" thru_hole %s (at %s %s) (size 1.8 1.8) (drill 1.0)\n'
                  '\t\t(layers "*.Cu" "*.Mask")\n%s\t\t(uuid "%s")\n\t)\n'
                  % (num, "rect" if num == "1" else "circle", x, y, nt, U()))
    return b

def reindent(body):
    return "\n".join(("\t" + ln if ln else ln) for ln in body.split("\n"))

ESP_PADS = ([("8", 7.62, -8.89), ("7", 7.62, -6.35), ("6", 7.62, -3.81), ("5", 7.62, -1.27),
             ("4", 7.62, 1.27), ("3", 7.62, 3.81), ("2", 7.62, 6.35), ("1", 7.62, 8.89)]
            + [("9", -7.62, -8.89), ("10", -7.62, -6.35), ("11", -7.62, -3.81), ("12", -7.62, -1.27),
               ("13", -7.62, 1.27), ("14", -7.62, 3.81), ("15", -7.62, 6.35), ("16", -7.62, 8.89)])
LCD_PADS = [(str(i + 1), 0.0, -8.89 + 2.54 * i) for i in range(8)]
MAX_PADS = [(str(i + 1), 0.0, -3.81 + 2.54 * i) for i in range(4)]

usb_tab = lambda: (L1(-4.5, -11.25, -4.5, -13.25) + L1(-4.5, -13.25, 4.5, -13.25)
                   + L1(4.5, -13.25, 4.5, -11.25))
none = lambda: ""

PARTS = {
  "ESP32-C3_SuperMini": dict(
      descr="ESP32-C3 SuperMini 22.5x18mm, 2x8 THT 2.54mm, rows 15.24mm. TOP view, USB-C at -Y, power on the RIGHT.",
      tags="esp32 c3 supermini module tht", attr="through_hole",
      silk=(-9, -11.25, 9, 11.25), pads=ESP_PADS, extra=usb_tab, reflayer="F.SilkS", drill="th",
      refy=-15.0),   # clear of the USB-C tab silk at y=-13.25
  "ST7789_169_8P": dict(
      descr="1.69in 240x280 ST7789 SPI LCD module, 1x8 THT 2.54mm. Pin1=GND.",
      tags="st7789 lcd display module tht", attr="through_hole",
      silk=(-1.75, -10.16, 1.75, 10.16), pads=LCD_PADS, extra=none, reflayer="F.SilkS", drill="th"),
  "MAX3232_MODULE_4P": dict(
      descr="MAX3232 RS-232 module, TTL side 1x4 THT 2.54mm. Pin1=VCC.",
      tags="max3232 rs232 uart module tht", attr="through_hole",
      silk=(-1.75, -5.08, 1.75, 5.08), pads=MAX_PADS, extra=none, reflayer="F.SilkS", drill="th"),
  "MountingHole_M3": dict(
      descr="Mounting hole 3.2mm for M3 screw, no silkscreen.",
      tags="mounting hole m3", attr="exclude_from_pos_files exclude_from_bom",
      silk=(None, -3.5, None, 3.5), pads=[("", 0.0, 0.0)], extra=none,
      reflayer="F.Fab", drill="np"),
}

for name, part in PARTS.items():
    txt = ('(footprint "%s"\n\t(version 20240108)\n\t(generator "pcbnew")\n\t(generator_version "8.0")\n'
           '\t(layer "F.Cu")\n\t(descr "%s")\n\t(tags "%s")\n\t(attr %s)\n%s)\n'
           % (name, part["descr"], part["tags"], part["attr"], fp_body(part, "REF**", name)))
    with open(os.path.join(PRETTY, name + ".kicad_mod"), "w", encoding="utf-8") as f:
        f.write(txt)

# ================================================================ BOARD
BX0, BY0, BX1, BY1 = 25.0, 25.0, 95.0, 70.0
LAYERS = "".join("\t\t(%s)\n" % s for s in [
    '0 "F.Cu" signal', '31 "B.Cu" signal', '32 "B.Adhes" user "B.Adhesive"',
    '33 "F.Adhes" user "F.Adhesive"', '34 "B.Paste" user', '35 "F.Paste" user',
    '36 "B.SilkS" user "B.Silkscreen"', '37 "F.SilkS" user "F.Silkscreen"',
    '38 "B.Mask" user', '39 "F.Mask" user', '40 "Dwgs.User" user "User.Drawings"',
    '41 "Cmts.User" user "User.Comments"', '42 "Eco1.User" user "User.Eco1"',
    '43 "Eco2.User" user "User.Eco2"', '44 "Edge.Cuts" user', '45 "Margin" user',
    '46 "B.CrtYd" user "B.Courtyard"', '47 "F.CrtYd" user "F.Courtyard"',
    '48 "B.Fab" user', '49 "F.Fab" user'])

pcb = ('(kicad_pcb\n\t(version 20240108)\n\t(generator "pcbnew")\n\t(generator_version "8.0")\n'
       '\t(general\n\t\t(thickness 1.6)\n\t\t(legacy_teardrops no)\n\t)\n\t(paper "A4")\n'
       '\t(layers\n%s\t)\n\t(setup\n\t\t(pad_to_mask_clearance 0)\n'
       '\t\t(allow_soldermask_bridges_in_footprints no)\n\t)\n' % LAYERS)

NETNAMES = ["GND", "+3V3", "LCD_SCL", "LCD_SDA", "LCD_RST",
            "LCD_DC", "LCD_CS", "LCD_BL", "UART_TX", "UART_RX"]
NETNO = {n: i + 1 for i, n in enumerate(NETNAMES)}
pcb += '\t(net 0 "")\n'
pcb += "".join('\t(net %d "%s")\n' % (NETNO[n], n) for n in NETNAMES)

def gr_line(x1, y1, x2, y2, layer="Edge.Cuts", w=0.1):
    return ('\t(gr_line (start %s %s) (end %s %s)\n\t\t(stroke (width %s) (type solid))\n'
            '\t\t(layer "%s")\n\t\t(uuid "%s")\n\t)\n' % (x1, y1, x2, y2, w, layer, U()))

R = 3.0
pcb += (gr_line(BX0 + R, BY0, BX1 - R, BY0) + gr_line(BX1, BY0 + R, BX1, BY1 - R)
        + gr_line(BX1 - R, BY1, BX0 + R, BY1) + gr_line(BX0, BY1 - R, BX0, BY0 + R))
for cx, cy, a0, a1 in [(BX0 + R, BY0 + R, 180, 270), (BX1 - R, BY0 + R, 270, 360),
                       (BX1 - R, BY1 - R, 0, 90), (BX0 + R, BY1 - R, 90, 180)]:
    pt = lambda a: (cx + R * math.cos(math.radians(a)), cy + R * math.sin(math.radians(a)))
    (sx, sy), (mx, my), (ex, ey) = pt(a0), pt((a0 + a1) / 2.0), pt(a1)
    pcb += ('\t(gr_arc (start %.4f %.4f) (mid %.4f %.4f) (end %.4f %.4f)\n'
            '\t\t(stroke (width 0.1) (type solid))\n\t\t(layer "Edge.Cuts")\n\t\t(uuid "%s")\n\t)\n'
            % (sx, sy, mx, my, ex, ey, U()))

U1N = {"1": "UART_TX", "2": "LCD_RST", "3": "LCD_CS", "4": "LCD_DC", "5": "LCD_SCL",
       "6": "+3V3", "7": "GND", "9": "LCD_BL", "10": "LCD_SDA", "11": "UART_RX"}
U2N = {"1": "GND", "2": "+3V3", "3": "LCD_SCL", "4": "LCD_SDA",
       "5": "LCD_RST", "6": "LCD_DC", "7": "LCD_CS", "8": "LCD_BL"}
U3N = {"1": "+3V3", "2": "GND", "3": "UART_TX", "4": "UART_RX"}
netmap = lambda d: {k: (NETNO[v], v) for k, v in d.items()}

#          ref  footprint               value                     x     y    rot  nets
PLACE = [("U1", "ESP32-C3_SuperMini", "ESP32-C3 SuperMini",    45.0, 47.5,  0, netmap(U1N)),
         ("U2", "ST7789_169_8P",      "ST7789 1.69in 240x280", 70.0, 47.5,  0, netmap(U2N)),
         ("U3", "MAX3232_MODULE_4P",  "MAX3232 module 4P",     45.0, 63.0, 90, netmap(U3N)),
         ("H1", "MountingHole_M3", "MountingHole_M3", BX0 + 4, BY0 + 4, 0, None),
         ("H2", "MountingHole_M3", "MountingHole_M3", BX1 - 4, BY0 + 4, 0, None),
         ("H3", "MountingHole_M3", "MountingHole_M3", BX0 + 4, BY1 - 4, 0, None),
         ("H4", "MountingHole_M3", "MountingHole_M3", BX1 - 4, BY1 - 4, 0, None)]

for ref, name, value, px, py, rot, nets in PLACE:
    part = PARTS[name]
    at = "%s %s %s" % (px, py, rot) if rot else "%s %s" % (px, py)
    pcb += ('\t(footprint "PlotBridge:%s"\n\t\t(layer "F.Cu")\n\t\t(uuid "%s")\n\t\t(at %s)\n'
            '\t\t(descr "%s")\n\t\t(tags "%s")\n\t\t(attr %s)\n%s\t)\n'
            % (name, U(), at, part["descr"], part["tags"], part["attr"],
               reindent(fp_body(part, ref, value, nets, rot))))

# ---------------------------------------------------------------- routing
# Hand-planned 2-layer route. B.Cu is the main layer (free under the modules);
# four nets that would otherwise cross are lifted to F.Cu. THT pads join both
# layers, so no vias are needed.
#   U3 pads after the 90-degree rotation, left to right:
#   1 VCC (41.19, 63)   2 GND (43.73, 63)   3 RX (46.27, 63)   4 TX (48.81, 63)
ROUTES = [
    # --- U1 <-> U2, through the channel between them
    ("GND",     "B.Cu", [(52.62, 41.15), (56, 41.15), (56, 38.61), (70, 38.61)]),
    ("+3V3",    "B.Cu", [(52.62, 43.69), (58, 43.69), (58, 41.15), (70, 41.15)]),
    ("LCD_SCL", "B.Cu", [(52.62, 46.23), (60, 46.23), (60, 43.69), (70, 43.69)]),
    ("LCD_CS",  "B.Cu", [(52.62, 51.31), (62, 51.31), (62, 53.85), (70, 53.85)]),
    ("LCD_DC",  "B.Cu", [(52.62, 48.77), (64, 48.77), (64, 51.31), (70, 51.31)]),
    ("LCD_RST", "F.Cu", [(52.62, 53.85), (66, 53.85), (66, 48.77), (70, 48.77)]),
    # LCD_SDA and LCD_BL leave U1 on the left column, so they loop around
    ("LCD_SDA", "F.Cu", [(37.38, 41.15), (33, 41.15), (33, 30), (68, 30),
                         (68, 46.23), (70, 46.23)]),
    ("LCD_BL",  "B.Cu", [(37.38, 38.61), (35.5, 38.61), (35.5, 67.5),
                         (70, 67.5), (70, 56.39)]),
    # --- U1 <-> U3 (below U1). Power branches off the U1 pads; the gap between
    #     U1's two pad columns is free copper on both layers.
    ("GND",     "B.Cu", [(52.62, 41.15), (39, 41.15), (39, 66), (43.73, 66), (43.73, 63)]),
    ("+3V3",    "B.Cu", [(52.62, 43.69), (50, 43.69), (50, 59.5), (41.19, 59.5), (41.19, 63)]),
    ("UART_TX", "B.Cu", [(52.62, 56.39), (52.62, 60.5), (46.27, 60.5), (46.27, 63)]),
    # UART_RX crosses LCD_BL's descent, so it is lifted to F.Cu
    ("UART_RX", "F.Cu", [(37.38, 43.69), (32, 43.69), (32, 66), (48.81, 66), (48.81, 63)]),
]
TRACK_W = 0.25
nseg = 0
for net, layer, pts in ROUTES:
    for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
        pcb += ('\t(segment (start %s %s) (end %s %s) (width %s) (layer "%s") (net %d)\n'
                '\t\t(uuid "%s")\n\t)\n' % (x1, y1, x2, y2, TRACK_W, layer, NETNO[net], U()))
        nseg += 1
pcb += ')\n'
with open(os.path.join(OUT, "PlotBridge.kicad_pcb"), "w", encoding="utf-8") as f:
    f.write(pcb)

# ================================================================ PROJECT / TABLES
pro = {
    "board": {"3dviewports": [], "design_settings": {"defaults": {}, "diff_pair_dimensions": [],
              "drc_exclusions": [], "rules": {}, "track_widths": [0.0, 0.25, 0.5],
              "via_dimensions": []}, "layer_presets": [], "viewports": []},
    "boards": [], "cvpcb": {"equivalence_files": []},
    "libraries": {"pinned_footprint_libs": [], "pinned_symbol_libs": []},
    "meta": {"filename": "PlotBridge.kicad_pro", "version": 1},
    "net_settings": {"classes": [{"bus_width": 12.0, "clearance": 0.2, "diff_pair_gap": 0.25,
        "diff_pair_via_gap": 0.25, "diff_pair_width": 0.2, "line_style": 0,
        "microvia_diameter": 0.3, "microvia_drill": 0.1, "name": "Default",
        "pcb_color": "rgba(0, 0, 0, 0.000)", "schematic_color": "rgba(0, 0, 0, 0.000)",
        "track_width": 0.25, "via_diameter": 0.8, "via_drill": 0.4, "wire_width": 6.0}],
        "meta": {"version": 3}, "net_colors": None, "netclass_assignments": None,
        "netclass_patterns": []},
    "pcbnew": {"last_paths": {"gencad": "", "idf": "", "netlist": "", "plot": "gerber/",
        "specctra_dsn": "", "step": "", "svg": "", "vrml": ""}, "page_layout_descr_file": ""},
    "schematic": {"legacy_lib_dir": "", "legacy_lib_list": [], "page_layout_descr_file": ""},
    "sheets": [[ROOT_UUID, "Root"]], "text_variables": {},
}
with open(os.path.join(OUT, "PlotBridge.kicad_pro"), "w", encoding="utf-8") as f:
    json.dump(pro, f, indent=2)
with open(os.path.join(OUT, "sym-lib-table"), "w", encoding="utf-8") as f:
    f.write('(sym_lib_table\n\t(version 7)\n\t(lib (name "PlotBridge")(type "KiCad")'
            '(uri "${KIPRJMOD}/PlotBridge.kicad_sym")(options "")(descr "PlotBridge module symbols"))\n)\n')
with open(os.path.join(OUT, "fp-lib-table"), "w", encoding="utf-8") as f:
    f.write('(fp_lib_table\n\t(version 7)\n\t(lib (name "PlotBridge")(type "KiCad")'
            '(uri "${KIPRJMOD}/PlotBridge.pretty")(options "")(descr "PlotBridge module footprints"))\n)\n')

print("generated: symbols=%d wires=%d labels=%d no_connect=%d footprints=%d parts_on_board=%d"
      % (len(SY), len(W), len(LB), len(NC), len(PARTS), len(PLACE)))
