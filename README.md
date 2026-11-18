# Flood Gauge

A cheap, deliberately low-tech water level sensor. A plastic bottle floats in a vertical pipe. As the water rises it lifts the bottle, and a ball chain over a pulley turns a magnet. A magnetic angle sensor reads the magnet through a sealed plastic wall, so nothing electrical touches water. An ESP32 kept somewhere dry (in the house or a shed) counts pulley turns and reports the water level over WiFi.

Built during the November 2026 San Francisco floods.

![Flood gauge strapped to a shed wall, with the sensor cable running inside](docs/view_yard.png)

**Interactive 3D model:** open [`web/index.html`](web/index.html) through a local web server (`cd web && python3 -m http.server`), then visit http://localhost:8000. It has views for the yard, pulley, sensor (X-ray), float and weights, inlet holes, and the shed interior, plus a water-depth slider and a storm simulation.

```
      sensor pod (sealed)                         ESP32 indoors / in shed
          ┌──┐   pulley                           ┌──────────────┐
          │▣ │◯  ← magnet on axle    Cat5 cable   │ ESP32 + PSU  │
          └──┘ ╱ ╲  ───────────────────────────── │ → Home Asst. │
   ═══ cap ═══╪═══╪══                             └──────────────┘
          ║   │   │ counterweight (outside pipe)
  3" ABS  ║   │   ▮
  pipe    ║ ┌─┴─┐
          ║ │   │ bottle float
  ~~~~~~~~║~│~~~│~~~~~~ water
          ║ └───┘
          ╚══ holes near bottom let water in
```

## How it works

1. **Stilling well.** A vertical 3" ABS (or PVC) pipe, black so it blends in, is strapped to a shed or house wall, fence post or stake. Three staggered rows of 12 mm holes in the bottom 100 mm let floodwater in. They also smooth out waves and keep debris away from the float.

   ![Inlet holes at the bottom of the pipe](docs/view_inlet.png)
2. **Float.** An empty 500–700 mL plastic bottle, no wider than 70 mm so it fits in 3" pipe (about 76 mm inside), with a little sand in the bottom so it hangs upright. It hangs from a ball chain down the centre of the pipe.
3. **Pulley.** The chain runs over a 3D-printed sprocket pulley at the top of the pipe. The ball pockets mean the chain can't slip when wet.
4. **Counterweight.** The other end of the chain hangs outside the pipe and keeps the chain tight, so the float follows the water back down. A short length of 1" ABS capped at both ends and filled with sand works well.
5. **Sensor.** A 6×2.5 mm diametric magnet sits in the end of the pulley axle. An AS5600 magnetic encoder in a sealed pod reads the axle angle through a 1.2 mm plastic wall.

   ![X-ray view of the sensor pod](docs/view_sensor.png)
6. **ESP32.** It counts full turns and adds the angle. One pulley turn equals 180 mm of chain, so the AS5600's 4096 steps per turn give about 0.04 mm per count. Expect about 1 mm accuracy in practice.

### How the weights balance

![Forces on the float and counterweight](docs/view_forces.png)

**The float has to be the heavier side.** An empty bottle weighs about 20 g, which isn't enough. Add sand until the bottle weighs about 150 g, and use a 100 g counterweight.

- **Dry pipe:** the float pulls down with 150 g and the counterweight pulls back with 100 g. The float wins by 50 g and rests on the bottom of the pipe.
- **Water arrives:** buoyancy has to supply the missing 50 g. A 66 mm bottle gets that from about 15 mm of submersion (50 cm³ of water). Above that the float lifts off and rides the surface.
- **Water drops:** the float's extra 50 g pulls it back down, and the counterweight rises. The chain stays tight in both directions, so the pulley never skips.

The rule:

```
float weight in air  >  counterweight  >  float weight − buoyancy (at the depth you want it to float)
```

Example: a 150 g float (bottle plus sand) with a 100 g counterweight. In air, the float has 50 g of net pull and drops to the bottom. In water, a 600 mL bottle gives up to about 600 g of lift, so it floats with only a few centimetres submerged.

## Parts to make

| Part | File | How to make |
|---|---|---|
| Head (pipe cap, pulley uprights, sensor pod) | `out/head.stl` / `.step` | 3D print, black ASA or PETG. Print sleeve-down with tree supports under the top plate. |
| Sprocket pulley | `out/pulley.stl` / `.step` | 3D print flat, 0.2 mm layers. No supports needed. |
| Sensor pod lid | `out/sensor_lid.stl` / `.step` | 3D print with the lip facing up. |
| Mounting plate | `out/mount_plate.dxf` / `.svg` | Laser cut (xTool P2) from 6 mm plywood or acrylic. Two hose clamps hold the pipe, and four screws attach it to the wall or post. |

Source: [`cad/flood_head.py`](cad/flood_head.py) (build123d). Edit the parameters at the top and run `python cad/flood_head.py` to regenerate everything in `out/`. Check `chain_pitch` against your actual chain first.

### Key dimensions

| | |
|---|---|
| Pipe OD | 88.9 mm (3" ABS DWV or 3" Sch40 PVC) |
| Chain | #10 ball chain, 4.5 mm balls, 6.0 mm pitch (measure yours) |
| Pulley | 30 pockets, 57.3 mm pitch diameter, 180 mm of chain per turn |
| Counterweight drop | 57.3 mm from pipe centre, just outside the pipe wall |
| Sensor wall | 1.2 mm. Magnet-to-chip distance about 2.5–3 mm, inside AS5600's 0.5–3 mm range |
| Fasteners | 2× M4 set screws (cap to pipe), 4× M3×10 self-tapping (pod lid), PG7 cable gland |

## Bill of materials

- 3" ABS (or PVC) pipe, tall enough to reach above the highest expected water. A 1.2 m length covers most yard flooding.
- 1" ABS pipe offcut and 2 end caps (counterweight), plus sand
- #10 ball chain, about 2× pipe length, plus 2 connectors
- 500–700 mL plastic bottle, ≤ 70 mm diameter (float)
- AS5600 breakout board and a 6×2.5 mm diametric neodymium magnet
- PG7 cable gland, a thin foam gasket or silicone, and a silica gel packet for the pod
- Outdoor Cat5e/Cat6 cable, run from the pod to where the ESP32 lives
- ESP32 (C3, S3 or classic) with a USB power supply
- 2 stainless hose clamps and 4 exterior screws

## Wiring: long cable to an indoor ESP32

![Cable through a wall gland to the ESP32 on a shelf inside the shed](docs/view_shed.png)

The cable leaves the sensor pod through a downward-facing PG7 gland. It then enters the shed through a second gland (PG9 or a 1/2" conduit gland) placed well above flood level. Leave a drip loop below the wall gland so water runs off instead of following the cable inside.

I2C (the AS5600's default interface) is unreliable past about 1 m. To keep the ESP32 inside the house or a shed, use one of these:

**Option A (simplest): PWM output.** Configure the AS5600's OUT pin for PWM output (register `CONF.OUTS = 10`). The breakout's DIR/PGO pins can stay at their defaults. Run 3.3 V, GND and OUT over one twisted pair of Cat5. The ESP32 measures the duty cycle (about 920 Hz) on any GPIO. This is reliable over 10–30 m. Put a 100 Ω series resistor and a small 1 nF capacitor at the ESP32 end.

**Option B: differential I2C.** Put a PCA9615 board at each end of the Cat5 run. You keep full I2C access, including the magnet-strength status bits, at 30 m or more.

Either way, at the ESP32:

```
level_mm = (turns * 4096 + raw_angle) / 4096 * 180  - zero_offset
```

- Sample at least every 0.5 s, so the pulley never turns more than half a revolution between samples. Floods rise far slower than that.
- Store `turns` in NVS (flash) every few minutes and at each change. The other option is to re-zero at boot when the ground is dry.
- Report to Home Assistant through ESPHome. The `as5600` component handles option B directly. For option A, use a `pulse_width` sensor plus a small lambda for turn counting.

## Siting

- Mount the pipe vertically against a house wall, fence post or a stake driven into the lowest spot of the yard where water collects. Low black pipe next to a house gets ignored.
- Leave the bottom of the pipe a few centimetres above the ground on a brick, or drill plenty of 10 mm holes in the bottom 10 cm. Then silt can't seal it.
- The counterweight drops as the water rises. Give it as much clear space below the cap as the float's travel.
- Put the cap's rain drains and the pod's cable gland facing down.

## Status

Concept and first CAD pass. Not yet printed or tested.
