"""Flood gauge head unit: pipe cap + pulley uprights + sealed AS5600 sensor pod,
ball-chain sprocket pulley, pod lid, and a laser-cut mounting plate.

Run:  python cad/flood_head.py   (writes STEP/STL/DXF into out/)
All dimensions in mm. Change parameters at the top and re-run.
"""
import math
from pathlib import Path
from build123d import *

OUT = Path(__file__).resolve().parent.parent / "out"

# ---------------- parameters ----------------
pipe_od = 88.9          # 3" ABS DWV and 3" Sch40 PVC share this OD (3.500")
pipe_clear = 0.6        # diametral slip clearance
cap_wall = 3.0
cap_depth = 30.0
plate_t = 4.0

ball_d = 4.5            # #10 ball chain ball diameter
chain_pitch = 6.0       # ball centre-to-centre: MEASURE YOUR CHAIN
link_w = 1.6            # groove for the links between balls
n_pockets = 30
pitch_c = n_pockets * chain_pitch          # chain travel per pulley turn (180 mm)
pitch_r = pitch_c / (2 * math.pi)
flange_r = pitch_r + 4.5
core_w = 6.0
flange_t = 2.0
pulley_w = core_w + 2 * flange_t
stub_d = 8.0
stub_len = 5.0
mag_d, mag_h = 6.2, 2.6                   # pocket for 6x2.5 diametric magnet

up_gap = 0.5            # pulley-flange to upright clearance per side
up_t = 5.0
up_w = 24.0
axis_x = -pitch_r       # float chain drops at x=0 (pipe centre)
axis_z = plate_t + flange_r + 6.0
cw_x = -2 * pitch_r     # counterweight chain drops outside the pipe
slot_w = stub_d + 0.4
up_y = pulley_w / 2 + up_gap + up_t / 2
up_top = axis_z + 10
chain_hole = 9.0

pod_wall = 1.2          # wall between magnet and AS5600 chip
pod_in = 26.0           # AS5600 breakout is ~23 mm square
pod_depth = 16.0
pod_rim = 5.0
pod_out = pod_in + 2 * pod_rim
pod_len = pod_wall + pod_depth
lid_t = 3.0

cap_ir = pipe_od / 2 + pipe_clear / 2
cap_or = cap_ir + cap_wall


def build_pulley():
    """Pulley with axis along Z (print orientation)."""
    p = Cylinder(pitch_r + 0.2, core_w)
    p += Pos(0, 0, core_w / 2 + flange_t / 2) * Cylinder(flange_r, flange_t)
    p += Pos(0, 0, -core_w / 2 - flange_t / 2) * Cylinder(flange_r, flange_t)
    p -= Cylinder(pitch_r + 3, link_w) - Cylinder(pitch_r - 0.6, link_w)
    for i in range(n_pockets):
        a = 2 * math.pi * i / n_pockets
        p -= Pos(pitch_r * math.cos(a), pitch_r * math.sin(a), 0) * Sphere(ball_d / 2 + 0.2)
    p += Pos(0, 0, pulley_w / 2 + stub_len / 2) * Cylinder(stub_d / 2, stub_len)
    p += Pos(0, 0, -pulley_w / 2 - stub_len / 2) * Cylinder(stub_d / 2, stub_len)
    p -= Pos(0, 0, pulley_w / 2 + stub_len - mag_h / 2) * Cylinder(mag_d / 2, mag_h)
    for i in range(5):
        a = 2 * math.pi * i / 5
        p -= Pos(pitch_r * 0.55 * math.cos(a), pitch_r * 0.55 * math.sin(a), 0) * Cylinder(5.5, 40)
    return p


def build_cap():
    with BuildPart() as cp:
        with BuildSketch():
            Circle(cap_or)
            with Locations((cw_x / 2 - 4.5, 0)):
                RectangleRounded(-cw_x + 9, 22, 6)
        extrude(amount=plate_t)
        with BuildSketch(Plane.XY.offset(-cap_depth)):
            Circle(cap_or)
            Circle(cap_ir, mode=Mode.SUBTRACT)
        extrude(amount=cap_depth + 1)
        for y in (up_y, -up_y):
            h = up_top - plate_t + 1
            with Locations((axis_x, y, plate_t - 1 + h / 2)):
                Box(up_w, up_t, h)
        for y in (up_y, -up_y):
            with Locations((axis_x, y, axis_z + 10)):
                Box(slot_w, up_t * 3, 20, mode=Mode.SUBTRACT)
            with Locations(Location((axis_x, y, axis_z), (90, 0, 0))):
                Cylinder(slot_w / 2, up_t * 3, mode=Mode.SUBTRACT)
        for x in (0, cw_x):
            with Locations((x, 0, plate_t / 2)):
                Cylinder(chain_hole / 2, plate_t * 3, mode=Mode.SUBTRACT)
        with Locations(*[(30 * math.cos(math.radians(a)), 30 * math.sin(math.radians(a)), plate_t / 2)
                         for a in (60, 120, 240, 300)]):
            Cylinder(2.5, plate_t * 3, mode=Mode.SUBTRACT)       # rain drains
        with Locations(Location((0, 0, -cap_depth / 2), (90, 0, 0))):
            Cylinder(1.7, cap_or * 2.2, mode=Mode.SUBTRACT)      # M4 set screws
    return cp.part


def build_pod():
    y0 = up_y + up_t / 2
    c = pod_in / 2 + pod_rim / 2
    with BuildPart() as pp:
        with Locations((axis_x, y0 + pod_len / 2, axis_z)):
            Box(pod_out, pod_len, pod_out)
        with Locations((axis_x, y0 + pod_wall + pod_depth / 2 + 0.01, axis_z)):
            Box(pod_in, pod_depth + 0.02, pod_in, mode=Mode.SUBTRACT)
        with Locations((axis_x, y0 + pod_wall + pod_depth / 2 + 1, axis_z - pod_out / 2 + pod_rim / 2)):
            Cylinder(12.5 / 2, pod_rim * 3, mode=Mode.SUBTRACT)  # PG7 gland, points down
        for dx in (-c, c):
            for dz in (-c, c):
                with Locations(Location((axis_x + dx, y0 + pod_len - 6, axis_z + dz), (90, 0, 0))):
                    Cylinder(1.25, 12.01, mode=Mode.SUBTRACT)    # M3 self-tap
    with BuildPart() as lp:
        with Locations((axis_x, y0 + pod_len + lid_t / 2, axis_z)):
            Box(pod_out, lid_t, pod_out)
        with Locations((axis_x, y0 + pod_len - 1, axis_z)):
            Box(pod_in - 0.6, 2, pod_in - 0.6)
            Box(pod_in - 4.6, 2.02, pod_in - 4.6, mode=Mode.SUBTRACT)
        for dx in (-c, c):
            for dz in (-c, c):
                with Locations(Location((axis_x + dx, y0 + pod_len + lid_t / 2, axis_z + dz), (90, 0, 0))):
                    Cylinder(1.7, lid_t * 3, mode=Mode.SUBTRACT)
    return pp.part, lp.part


def build_mount_plate():
    """2D outline for laser cutting (6 mm plywood/acrylic)."""
    with BuildSketch() as ms:
        RectangleRounded(120, 260, 8)
        with Locations((-45, 115), (45, 115), (-45, -115), (45, -115)):
            Circle(2.6, mode=Mode.SUBTRACT)
        for yy in (70, -70):
            with Locations((-38, yy), (38, yy)):
                SlotOverall(16, 5, rotation=90, mode=Mode.SUBTRACT)
    return ms.sketch


if __name__ == "__main__":
    OUT.mkdir(exist_ok=True)
    pulley = build_pulley()
    pod, lid = build_pod()
    head = build_cap().fuse(pod).clean()
    for name, part in (("head", head), ("pulley", pulley), ("sensor_lid", lid)):
        export_step(part, OUT / f"{name}.step")
        export_stl(part, OUT / f"{name}.stl")
    plate = build_mount_plate()
    exp = ExportDXF()
    exp.add_shape(plate)
    exp.write(OUT / "mount_plate.dxf")
    print(f"pulley: {pitch_c:.0f} mm of chain per turn, {pitch_c / 4096:.3f} mm per AS5600 count")
