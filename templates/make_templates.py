"""Generate printable 1:1 drilling templates (US Letter PDF), no dependencies.

    python3 templates/make_templates.py

Writes templates/cap_template.pdf and templates/pipe_inlet_template.pdf.
Print at 100% ("Actual size"), then check the 50 mm scale bar with a ruler.
Dimensions match cad/flood_head.py.
"""
import math
from pathlib import Path

HERE = Path(__file__).resolve().parent
MM = 72 / 25.4
PAGE_W, PAGE_H = 612, 792  # US Letter, points

# --- geometry (mm), keep in sync with cad/flood_head.py ---
CAP_OD = 99.0                       # 3" ABS DWV cap: measure yours
CHAIN_HOLE = 10.0                   # 3/8" drill
BOLT_HOLE = 4.5                     # 3/16" drill, M4 or #8 bolts
BOLTS = [(8, 9), (8, -9), (-14, 0)]
PITCH_R = 32 * 6.0 / (2 * math.pi)  # pulley pitch radius
BR_X0, BR_X1, BR_W = 14.0, -2 * PITCH_R - 9.0, 30.0
CW_X = -2 * PITCH_R

PIPE_OD = 88.9
CIRC = math.pi * PIPE_OD            # 279.3 mm
INLET_D = 12.7                      # 1/2" drill
ROWS = [(20, 8.7), (50, 26.2), (80, 8.7)]   # (height from bottom, first-hole offset)
PER_ROW = 8


class Page:
    def __init__(self):
        self.ops = []

    def mm(self, x, y):
        return x * MM, y * MM

    def line(self, x1, y1, x2, y2, w=0.5, dash=None, gray=0):
        d = f"[{dash[0]} {dash[1]}] 0 d" if dash else "[] 0 d"
        a, b = self.mm(x1, y1)
        c, e = self.mm(x2, y2)
        self.ops.append(f"{gray} G {w} w {d} {a:.2f} {b:.2f} m {c:.2f} {e:.2f} l S")

    def rect(self, x, y, w, h, lw=0.5, dash=None, gray=0):
        d = f"[{dash[0]} {dash[1]}] 0 d" if dash else "[] 0 d"
        a, b = self.mm(x, y)
        self.ops.append(f"{gray} G {lw} w {d} {a:.2f} {b:.2f} {w*MM:.2f} {h*MM:.2f} re S")

    def circle(self, cx, cy, r, lw=0.6, dash=None, fill=None, gray=0):
        k = 0.5523 * r
        p = lambda x, y: f"{(cx+x)*MM:.2f} {(cy+y)*MM:.2f}"
        d = f"[{dash[0]} {dash[1]}] 0 d" if dash else "[] 0 d"
        path = (f"{p(r,0)} m {p(r,k)} {p(k,r)} {p(0,r)} c {p(-k,r)} {p(-r,k)} {p(-r,0)} c "
                f"{p(-r,-k)} {p(-k,-r)} {p(0,-r)} c {p(k,-r)} {p(r,-k)} {p(r,0)} c")
        op = "B" if fill is not None else "S"
        fs = f"{fill} g " if fill is not None else ""
        self.ops.append(f"{gray} G {fs}{lw} w {d} {path} {op}")

    def cross(self, x, y, s=3, w=0.4):
        self.line(x - s, y, x + s, y, w)
        self.line(x, y - s, x, y + s, w)

    def text(self, x, y, s, size=9, bold=False, center=False):
        s = s.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        font = "F2" if bold else "F1"
        if center:
            x -= len(s) * size * 0.25 / MM
        a, b = self.mm(x, y)
        self.ops.append(f"0 g BT /{font} {size} Tf {a:.2f} {b:.2f} Td ({s}) Tj ET")

    def scale_bar(self, x, y, label="Scale check: this bar must measure 50 mm"):
        self.line(x, y, x + 50, y, 1.2)
        for i in range(0, 51, 10):
            self.line(x + i, y, x + i, y + (3 if i % 50 else 5), 0.8)
        self.text(x, y - 5, label, 8)


def write_pdf(path, pages):
    objs = []
    objs.append("<< /Type /Catalog /Pages 2 0 R >>")
    kids = " ".join(f"{5 + 2*i} 0 R" for i in range(len(pages)))
    objs.append(f"<< /Type /Pages /Kids [{kids}] /Count {len(pages)} >>")
    objs.append("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>")
    objs.append("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>")
    for i, pg in enumerate(pages):
        stream = "\n".join(pg.ops)
        objs.append(f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {PAGE_W} {PAGE_H}] "
                    f"/Resources << /Font << /F1 3 0 R /F2 4 0 R >> >> /Contents {6 + 2*i} 0 R >>")
        objs.append(f"<< /Length {len(stream.encode('latin-1'))} >>\nstream\n{stream}\nendstream")
    out = b"%PDF-1.4\n"
    offsets = []
    for n, o in enumerate(objs, 1):
        offsets.append(len(out))
        out += f"{n} 0 obj\n{o}\nendobj\n".encode("latin-1")
    xref = len(out)
    out += f"xref\n0 {len(objs)+1}\n0000000000 65535 f \n".encode()
    for off in offsets:
        out += f"{off:010d} 00000 n \n".encode()
    out += f"trailer\n<< /Size {len(objs)+1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode()
    path.write_bytes(out)


def cap_page():
    pg = Page()
    W = PAGE_W / MM
    pg.text(15, 262, "Flood Gauge: cap drilling template", 16, bold=True)
    pg.text(15, 254, "Fits the top of a 3 in. ABS DWV cap. Print at 100% (Actual size) and check the scale bar.", 9)
    pg.text(15, 249, "Cut along the solid circle, tape it centred on the cap, centre-punch each cross, then drill.", 9)
    cx, cy = 90, 160
    # cap outline (cut line) and bracket footprint (reference only)
    pg.circle(cx, cy, CAP_OD / 2, lw=1.0)
    pg.rect(cx + BR_X1, cy - BR_W / 2, BR_X0 - BR_X1, BR_W, lw=0.4, dash=(3, 2), gray=0.55)
    pg.cross(cx, cy, 6, 0.3)
    # holes
    pg.circle(cx, cy, CHAIN_HOLE / 2, lw=0.8)
    pg.cross(cx, cy, 2.5)
    for bx, by in BOLTS:
        pg.circle(cx + bx, cy + by, BOLT_HOLE / 2, lw=0.8)
        pg.cross(cx + bx, cy + by, 2)
    # counterweight drop point (not drilled: it is on the bracket tab past the cap edge)
    pg.circle(cx + CW_X, cy, 1.2, lw=0.4, fill=0.5, gray=0.5)
    # callouts
    pg.line(cx - 3, cy + 4, cx - 25, cy + 70, 0.3)
    pg.text(cx - 70, cy + 72, "Float chain: 10 mm (3/8 in.) drill", 9, bold=True)
    pg.line(cx + 10, cy - 10, cx + 38, cy - 30, 0.3)
    pg.text(cx + 39, cy - 31, "Bracket bolts (3x):", 9, bold=True)
    pg.text(cx + 39, cy - 36, "4.5 mm (3/16 in.) drill", 9, bold=True)
    pg.line(cx + CW_X, cy - 2, cx + CW_X - 4, cy - 72, 0.3)
    pg.text(15, cy - 76, "Counterweight chain hangs here, past the cap edge (no hole)", 8)
    pg.text(cx - 46, cy - BR_W / 2 - 4, "dashed: printed bracket footprint", 7)
    # orientation
    pg.line(cx - 70, cy - 58, cx + 70, cy - 58, 1.5)
    pg.text(cx, cy - 64, "WALL / SHED SIDE", 9, bold=True, center=True)
    pg.text(cx + 10, cy + 54, "sensor pod side (away from wall)", 8)
    pg.scale_bar(20, 30)
    pg.text(20, 20, "Cap OD assumed 99 mm. If your cap differs, centre the template by the cross, not the outline.", 8)
    return pg


def pipe_page():
    pg = Page()
    pg.text(15, 262, "Flood Gauge: inlet hole template (bottom of 3 in. pipe)", 16, bold=True)
    pg.text(15, 254, "Print at 100% (Actual size). Cut out strips A and B and tape them end to end (B's left edge on A's right edge).", 9)
    pg.text(15, 249, "Wrap round the bottom of the pipe with the BOTTOM EDGE flush with the pipe end. The strip should meet itself exactly.", 9)
    pg.text(15, 244, f"Drill 24 holes, 12.7 mm (1/2 in.). Pipe circumference {CIRC:.1f} mm; strip height 110 mm.", 9)
    half = CIRC / 2
    H = 110
    for idx, (label, x0, ybase) in enumerate((("A", 0.0, 130.0), ("B", half, 10.0))):
        ox = 15  # page margin
        oy = ybase
        pg.rect(ox, oy, half, H, lw=0.9)
        pg.line(ox, oy, ox + half, oy, 2.0)
        pg.text(ox + 2, oy + 2.5, "BOTTOM EDGE - flush with pipe end", 7, bold=True)
        pg.text(ox + half / 2, oy + H - 8, f"Strip {label}", 12, bold=True, center=True)
        if label == "A":
            pg.text(ox + half - 32, oy + H - 16, "join to B ->", 8)
        else:
            pg.text(ox + 2, oy + H - 16, "<- join to A", 8)
            pg.text(ox + half - 36, oy + H - 16, "meets A's left end", 8)
        for h, first in ROWS:
            for k in range(PER_ROW):
                x = first + k * CIRC / PER_ROW
                if x0 <= x < x0 + half:
                    hx = ox + (x - x0)
                    pg.circle(hx, oy + h, INLET_D / 2, lw=0.7)
                    pg.cross(hx, oy + h, 2)
        for h, _ in ROWS:
            pg.text(ox + half + 2, oy + h - 1, f"{h} mm", 7)
    pg.scale_bar(160, 127, "must measure 50 mm")
    return pg


if __name__ == "__main__":
    write_pdf(HERE / "cap_template.pdf", [cap_page()])
    write_pdf(HERE / "pipe_inlet_template.pdf", [pipe_page()])
    print("wrote", HERE / "cap_template.pdf", HERE / "pipe_inlet_template.pdf")
