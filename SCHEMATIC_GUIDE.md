# KiCad Schematic Guide — 5×5 Flip-Disc Driver Board

**What this document is:** a step-by-step guide for capturing the schematic of the 5×5 flip-disc driver board in **KiCad 10+**, using the **default KiCad libraries** wherever possible. Follow it top to bottom. Every net name, pin number, and part value here is the authoritative reference — firmware and PCB layout must agree with this document.

**What the board does (30-second version):** a Raspberry Pi Pico 2 W shifts a 24-bit control frame into three 74HC595 shift registers. Their outputs set the direction/state of five TB6612FNG dual H-bridges, which drive 10 matrix lines (5 rows + 5 columns). Each of the 25 off-board coils sits between one row line and one column line; pulsing one row and one column with opposite polarity for ~1 ms flips exactly one disc, which then latches mechanically with zero power. Everything runs from a single regulated 12 V supply.

---

## 0. Design changes vs. the original spec

Two deviations from the original spec document — both are **included in this guide already**, listed here so nobody re-introduces the old versions:

1. **Fuse added.** A fuse now sits between the barrel jack and everything else, so a shorted coil wire, a failed driver IC, or a wiring mistake blows a ₹10 fuse instead of frying the board.
2. **RGB LED removed.** Replaced with two plain 5 mm LEDs:
   - **D_PWR (green):** wired straight from the 3.3 V rail through a resistor — lights whenever the board is alive, zero firmware involvement.
   - **D_ACT (red):** on **GP10, active-high** — firmware turns it on while discs are flipping.
   - GP11 and GP12 are now **free/spare** GPIOs.

---

## 1. Project setup

1. Open KiCad → **File → New Project** → name it (e.g. `flipdisk-driver`). This creates the `.kicad_pro`, `.kicad_sch`, and `.kicad_pcb` files.
2. Open the **Schematic Editor**. Everything in this guide happens there.
3. Keep the default 50 mil grid for placing symbols and drawing wires. Never wire on a finer grid — off-grid pins cause "unconnected" ERC errors that are miserable to find.
4. Useful keys: `A` add symbol, `W` wire, `L` net label, `P` power symbol (in the add-symbol dialog, power symbols live in the `power` library), `C` copy, `E` edit.

**One schematic sheet is enough** for this design (~9 ICs). If you prefer, split into hierarchical sheets (power / MCU / drivers), but a single A3 sheet keeps it simple and this guide assumes that.

---

## 2. Symbol & footprint shopping list

Everything below is in the **default KiCad library** except the Pico — see §3 for that one download.

| Part | Symbol (library:name) | Footprint | Notes |
|---|---|---|---|
| Pico 2 W | `MCU_RaspberryPi:RaspberryPi_Pico_W` | pick a **THT / pin-socket** footprint variant, not `_SMD_HandSolder` | native in KiCad 9.0+/10.0+ default library — see §3 |
| TB6612FNG ×5 | `Driver_Motor:TB6612FNG` | `Package_SO:SSOP-24_5.3x8.2mm_P0.65mm` (pre-assigned) | dual H-bridge |
| 74HC595 ×3 | `74xx:74HC595` | `Package_DIP:DIP-16_W7.62mm_Socket` (THT, socketable) or `Package_SO:SOIC-16_3.9x9.9mm_P1.27mm` (SMD) | shift register |
| R-78E5.0-1.0 | `Regulator_Switching:R-78E5.0-1.0` | `Converter_DCDC:Converter_DCDC_RECOM_R-78E-0.5_THT` | the -0.5 and -1.0 share the identical SIP-3 package, so the -0.5 footprint is correct. The symbol should already have it assigned. |
| Barrel jack | `Connector:Barrel_Jack` | `Connector_BarrelJack:BarrelJack_Horizontal` | 5.5×2.1 mm center-positive |
| Fuse F1 | `Device:Fuse` | pick from the `Fuse` footprint library to match the holder you buy (5×20 mm holder, e.g. a Schurter 0031-series horizontal open holder) | see §5.1 |
| SS34 | `Device:D_Schottky` | `Diode_SMD:D_SMC` (DO-214AB) | reverse-polarity protect |
| SS14 (or 1N5819) | `Device:D_Schottky` | `Diode_SMD:D_SMA` (SS14) or `Diode_THT:D_DO-41_SOD81_P10.16mm_Horizontal` (1N5819) | 5V→VSYS diode |
| Screw terminals ×2 | `Connector:Screw_Terminal_01x05` | `TerminalBlock:TerminalBlock_bornier-5_P5.08mm` | coil matrix out |
| Tactile buttons ×4 | `Switch:SW_Push` | `Button_Switch_THT:SW_PUSH_6mm` | RESET/CLEAR/FUNC1/FUNC2 |
| LEDs ×2 | `Device:LED` | `LED_THT:LED_D5.0mm` | green + red |
| Resistors | `Device:R` | `Resistor_THT:R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal` (or 0805 SMD) | 330 Ω ×2, 10 kΩ ×1 |
| Electrolytic caps | `Device:C_Polarized` (`CP`) | 1000 µF: `Capacitor_THT:CP_Radial_D10.0mm_P5.00mm` · 100 µF: `Capacitor_THT:CP_Radial_D6.3mm_P2.50mm` | check your actual can diameter when you buy them |
| Ceramic caps | `Device:C` | 0.1 µF: `Capacitor_SMD:C_0805_2012Metric` · 10 µF & 22 µF: `Capacitor_SMD:C_1206_3216Metric` (or THT disc if you prefer) | decoupling |
| Test header 1×8 | `Connector_Generic:Conn_01x08` | `Connector_PinHeader_2.54mm:PinHeader_1x08_P2.54mm_Vertical` | debug/bodge |
| Mounting holes ×4 | `Mechanical:MountingHole` | `MountingHole:MountingHole_3.2mm_M3` | M3 |
| Power symbols | `power:+3V3`, `power:+5V`, `power:GND`, `power:PWR_FLAG` | n/a | see §4 |

**Footprint tip:** most symbols above come with a footprint pre-assigned. For the ones that don't (resistors, caps, LEDs, buttons, headers), assign them either per-symbol (symbol properties → Footprint field) or all at once later with **Tools → Assign Footprints**.

---

## 3. Raspberry Pi Pico symbol + footprint — no download needed on KiCad 10

Good news, and a correction to an earlier draft of this guide: **the Pico family is natively bundled in KiCad's official default libraries as of a June 2024 library update**, present in **KiCad 9.0+ and 10.0+**. It was imported from the community `ki-lime-pi-pico` project directly into the official `MCU_RaspberryPi` symbol library (grouped under "MCU_Module" in the symbol chooser, alongside Arduino/ESP32 boards). Nothing to install.

**Pico 2 W has the identical pinout and board outline as the Pico W** (Raspberry Pi's own documentation confirms this), so the `RaspberryPi_Pico_W` symbol/footprint set is the correct one to use — there isn't a separately-named "Pico 2 W" symbol, and you don't need one.

1. **Symbol:** `MCU_RaspberryPi:RaspberryPi_Pico_W`. Ignore the `_Debug` and `_Extensive` variants unless you specifically want SWD debug pins or every test pad broken out — plain `RaspberryPi_Pico_W` is enough here.
2. **Footprint:** the default assigned footprint is `Module:RaspberryPi_Pico_W_SMD_HandSolder`, meant for soldering the module flat onto the PCB. **This board sockets the Pico instead**, so after placing the symbol, open its footprint field / use the footprint chooser and pick the **THT / pin-socket variant** (look for a footprint with "PinSocket" or "THT" in the name in the same library). That gives the PCB two rows of **female pin sockets**; the Pico itself keeps (or gets) male header pins and plugs in.
3. (Optional) the matching 3D model ships too — it'll show automatically once the right footprint is assigned.

**If you ever need a library that isn't bundled** (not the case here, just for future reference): Preferences → Manage Symbol/Footprint Libraries → Add existing library, pointing at a folder outside KiCad's own install directory so updates don't wipe it.

---

## 4. Net names & power symbols (read before wiring)

**Wiring philosophy — don't over-label:**
- If two parts sit right next to each other and nothing else taps that connection, just draw a **plain wire**. Don't name it.
- If a net has a real KiCad power symbol (`GND`, `+3V3`, `+5V`), use the **power symbol**, not a text label — cleaner, and ERC understands it natively.
- Only use a **global label** for a net that (a) has no built-in power symbol, and (b) genuinely needs to reach far-apart parts of the sheet without a physically drawn wire (e.g. `VM`, and later `STBY`/`SR_CLK`/`SR_LATCH` and the 20 driver-input nets). This is a single-sheet design, so global labels and local net labels behave the same — either works, but global label is the natural choice since you'll likely reuse the habit if you ever split into hierarchical sheets later.

With that in mind, here are the nets that actually need a label (global label, unless a power symbol exists):

| Net | Label type | What it is |
|---|---|---|
| `VM` | global label | main coil rail, ~11.6 V, after SS34. Feeds all TB6612 VM pins + buck input — fans out far, needs a label |
| `+5V` | power symbol | R-78E output. Use `power:+5V` |
| `+3V3` | power symbol | Pico's 3V3OUT. All logic power. Use `power:+3V3` |
| `GND` | power symbol | single ground net, use `power:GND` everywhere. (Star topology is a **layout** rule, not schematic — one GND net here.) |
| `SR_DATA`, `SR_CLK`, `SR_LATCH` | global label | Pico → shift register control (fans out to 3 chips) |
| `SR1_Q7S`, `SR2_Q7S` | plain wire | daisy-chain link between adjacent 595s — no label needed, they sit next to each other |
| `STBY` | global label | Pico GP5 → all 5 TB6612 standby pins |
| `U1_AIN1` … `U5_BIN2` | global label | 20 driver input nets (naming: chip + pin) — 595 and driver aren't adjacent |
| `R0`–`R4`, `C0`–`C4` | global label | the 10 matrix drive lines — driver chip to screw terminal, not adjacent |
| `BTN_CLEAR`, `BTN_FUNC1`, `BTN_FUNC2` | plain wire (or label if far) | buttons — label only if you place them far from the Pico |
| `LED_ACT` | plain wire (or label if far) | GP10 → red LED resistor |
| — | plain wire, no name | jack→fuse, fuse→diode, diode→VM, buck-out→next-diode, diode→VSYS — all adjacent, don't label these |
| `TP1`–`TP4` | global label | spare 595 outputs → test header |

Everything not in this table (short adjacent hops) should just be a plain unnamed wire — see §5.1 for the concrete example.

**PWR_FLAG — do this or ERC will scream:** KiCad's ERC wants every power net to be *driven* by something it recognizes as a source. Nets that come from connectors/diodes/regulators aren't automatically recognized. Place a `power:PWR_FLAG` symbol touching each of: `+12V_IN` (or `+12V_F`), `VM`, `+5V`, `GND`, and — if your Pico symbol's 3V3 pin isn't of type "power output" — `+3V3`. It's a zero-component ERC marker, nothing more.

---

## 5. Schematic capture, section by section

Work through these in order. Reference designators used throughout: U1–U5 = TB6612, U6–U8 = 74HC595, U9 = R-78E, A1 = Pico, D1 = SS34, D2 = SS14, D3 = green LED, D4 = red LED, F1 = fuse, J1 = barrel jack, J2/J3 = screw terminals, J4 = test header, SW1–SW4 = buttons.

### 5.1 Power input: jack → fuse → reverse protection → VM

*What it does: takes 12 V in, survives a reversed adapter, and blows a cheap fuse instead of the board when something shorts.*

Wire, left to right:

```
J1 (Barrel_Jack) tip ──[+12V_IN]── F1 (Fuse) ──[+12V_F]── D1 SS34 anode ▷|── [VM]
J1 sleeve ── GND
```

1. **J1 barrel jack** — the `Connector:Barrel_Jack` symbol has pin 1 (tip) and pin 2 (sleeve). Tip = `+12V_IN`, sleeve = `GND`. Center-positive.
2. **F1 fuse** — `Device:Fuse`, in series, first thing after the jack so it protects *everything* downstream including the SS34 itself.
   - **Rating: 2 A slow-blow (time-delay, marked "T2A"), 5×20 mm glass cartridge in a PCB holder.** Why 2 A: normal average draw is well under 0.5 A (coil pulses are 0.64 A for 1 ms at low duty; Pico + logic < 0.3 A), so 2 A never nuisance-trips, but a hard short pulls the supply's full current and pops it fast. Why slow-blow: the 1000 µF bulk cap draws a large inrush spike at plug-in; a fast fuse could blow on that alone.
   - **Use a fuse holder, not a soldered fuse** — the whole point is replacing it in seconds. Buy holder + a few spare T2A fuses.
   - *Alternative:* a resettable PTC polyfuse (`Device:Polyfuse`, e.g. 1.35 A hold / 2 A trip, like a Bourns MF-R135) self-recovers after cooling — nice for a demo booth, but trips slower and its resistance eats a bit of voltage. Either is acceptable; the glass fuse is the default here.
3. **D1 SS34** — `Device:D_Schottky`, anode to `+12V_F`, cathode to `VM`. If the adapter is wired backwards, no current flows, nothing dies. Costs ~0.3–0.4 V, so `VM` ≈ 11.6 V. (Schottky specifically because of that low drop — a regular 1N4007 would waste ~0.7 V and more heat.)
4. **Bulk capacitors on VM** (all `Device:C_Polarized`, + terminal to VM, − to GND):
   - **C1: 1000 µF / 25 V** — the energy reservoir for coil pulses. A 0.64 A × 1 ms pulse sags it only ~0.6 V, so pulses never brown-out the rail.
   - **C2, C3: 100 µF / 25 V** — local reservoirs; in layout they go at the two ends of the TB6612 row.
5. Add a **text note** on the schematic near J1: `12 V REGULATED ONLY — 2 A` (this also goes on the silkscreen later). An unregulated brick can idle at 16–18 V and instantly kills all five TB6612s (13.5 V absolute max).

### 5.2 Buck converter: 12 V → 5 V

*What it does: makes the 5 V rail for the Pico. It's a switching module in a 3-pin 7805 pinout, so no inductor design, no heatsink — a linear 7805 dropping 7 V would cook.*

`U9 = Regulator_Switching:R-78E5.0-1.0`. Three pins:

| R-78E pin | Connect to |
|---|---|
| VI (in) | `VM` |
| GND | `GND` |
| VO (out) | `+5V` |

- **C4: 10 µF ceramic** from VI to GND (input decoupling).
- **C5: 22 µF ceramic** from VO to GND (output stability).

> If your KiCad's symbol chooser can't find `R-78E5.0-1.0`, the 500 mA sibling `R-78E5.0-0.5` is the identical symbol/package — place it and just edit the Value field to `R-78E5.0-1.0`. (Both are in the official lib.)

### 5.3 5 V → Pico VSYS diode

*What it does: lets the board's 5 V and a plugged-in USB cable coexist. The Pico has an internal diode from USB VBUS to VSYS; this diode mirrors it from the board side. Whichever source is higher wins, neither backfeeds the other. USB is only ever used for flashing — never for powering the coils.*

```
+5V ── D2 (SS14/1N5819) anode ▷|── [VSYS_IN] ── Pico VSYS (pin 39)
```

### 5.4 The Pico 2 W

*What it does: runs the firmware, provides the 3.3 V logic rail from its onboard regulator, and (later) WiFi. It is socketed so it can be pulled and replaced.*

Place the Pico symbol (A1) and connect:

| Pico pin # | Name | Connect to | Why |
|---|---|---|---|
| 39 | VSYS | `VSYS_IN` (from D2) | board power in |
| 36 | 3V3(OUT) | `+3V3` power symbol | sources the entire logic rail (595s + TB6612 VCC + green LED). Total load < 25 mA — trivial for the onboard regulator |
| 37 | 3V3_EN | **leave unconnected** | internal pull-up keeps the regulator enabled |
| 30 | RUN | SW1 (RESET) other side to `GND` | pulling RUN low resets the chip. Internal pull-up — no external resistor needed |
| 3, 8, 13, 18, 23, 28, 33, 38 | GND | `GND` | connect **all** of them |
| 4 | GP2 | `SR_DATA` | serial data into the 595 chain |
| 5 | GP3 | `SR_CLK` | shift clock (all three 595s) |
| 6 | GP4 | `SR_LATCH` | latch clock (all three 595s) |
| 7 | GP5 | `STBY` | master enable for all five drivers |
| 9 | GP6 | `BTN_CLEAR` | button, active-low |
| 10 | GP7 | `BTN_FUNC1` | button, active-low |
| 11 | GP8 | `BTN_FUNC2` | button, active-low |
| 14 | GP10 | `LED_ACT` | red activity LED, active-high |
| 40 | VBUS | leave unconnected | USB 5 V — intentionally unused |
| everything else | GP0/1, GP9, GP11–GP28, ADC_VREF, AGND | leave unconnected | spares (AGND may go to GND if your symbol combines it) |

**R1: 10 kΩ from `STBY` to `GND`.** This is the single most important passive on the board: at power-up, before firmware configures GP5, the pin floats — the pull-down guarantees STBY is low, which forces **every driver output Hi-Z no matter what garbage the 595s woke up containing**. Without it, a random powered-on coil would cook itself in seconds.

### 5.5 Buttons

*What they do: RESET restarts the Pico (needed for hold-BOOTSEL-tap-RESET reflashing, since the board runs on 12 V, not USB). The other three are firmware inputs.*

All four are `Switch:SW_Push`, one side to the signal, other side to `GND`:

| Ref | Label | Signal |
|---|---|---|
| SW1 | RESET | Pico RUN (pin 30) |
| SW2 | CLEAR | `BTN_CLEAR` (GP6) |
| SW3 | FUNC1 | `BTN_FUNC1` (GP7) |
| SW4 | FUNC2 | `BTN_FUNC2` (GP8) |

No external resistors — GP6/7/8 use the Pico's internal pull-ups (enable in firmware), RUN has one built in. Buttons read LOW when pressed. Debounce in firmware.

### 5.6 Indicator LEDs (simplified — two plain LEDs)

*What they do: green = "board has power and the Pico's 3.3 V regulator is up" — pure hardware, zero firmware. Red = "discs are flipping" — firmware toggles it.*

```
D3 (green):  +3V3 ── R2 330 Ω ── LED anode ▷|── GND        (always on)
D4 (red):    LED_ACT (GP10) ── R3 330 Ω ── LED anode ▷|── GND   (active-HIGH)
```

- Green: (3.3 V − 2.0 Vf) / 330 Ω ≈ 4 mA — gently lit, negligible load on the 3.3 V rail.
- Red: GPIO high sources ~4 mA — well within a GPIO's capability, no drive-strength changes needed.
- At boot GP10 is Hi-Z → red LED off. Correct default.

### 5.7 Shift registers — 3× 74HC595

*What they do: turn 3 Pico pins into 24 outputs. Bits are clocked in serially on SR_CLK, and nothing changes on the outputs until SR_LATCH pulses — so the drivers only ever see complete, valid frames, never half-shifted garbage.*

Place three `74xx:74HC595` (U6, U7, U8). The KiCad symbol uses NXP-style pin names; the spec used TI-style. Same chip, same pin numbers:

| KiCad symbol name | TI datasheet name | Pin # | Connect to (all three chips unless noted) |
|---|---|---|---|
| DS | SER | 14 | U6: `SR_DATA` · U7: `SR1_Q7S` · U8: `SR2_Q7S` |
| SHCP | SRCLK | 11 | `SR_CLK` |
| STCP | RCLK | 12 | `SR_LATCH` |
| OE (inverted) | OE̅ | 13 | `GND` — outputs always enabled (safety is handled by STBY, not here) |
| MR (inverted) | SRCLR̅ | 10 | `+3V3` — never hardware-reset |
| Q7' | QH′ | 9 | U6: `SR1_Q7S` · U7: `SR2_Q7S` · U8: leave unconnected |
| Q0–Q7 | QA–QH | 15, 1–7 | driver inputs / test points, per the map in §5.9 |
| VCC | VCC | 16 | `+3V3` |
| GND | GND | 8 | `GND` |

Decoupling: **one 0.1 µF ceramic per chip**, VCC to GND (C6–C8).

Chain order matters for firmware: `SR_DATA` enters U6; U6's Q7' feeds U7; U7's Q7' feeds U8. The **last bit you shift ends up in U6**.

### 5.8 Coil drivers — 5× TB6612FNG

*What they do: each chip is a dual H-bridge. We use it unconventionally: instead of connecting a motor across a bridge's two outputs, we take **one output per channel** (AO1, BO1) as an independent tri-state line that can source 12 V, sink to GND, or float. Ten such lines = the 5×5 matrix. The chip's built-in flyback diodes absorb the coil's inductive kick when a pulse ends, so no external diodes are needed.*

Place five `Driver_Motor:TB6612FNG` (U1–U5). The KiCad symbol is correct and handles a quirk for you: the chip doubles-up pins (e.g. AO1 is physically pins 1 *and* 2), and the symbol stacks the duplicates behind one visible pin — connect the visible pin and both physical pins are connected.

**Identical connections on all five chips:**

| Symbol pin | Pin #(s) | Connect to | Why |
|---|---|---|---|
| VM1, VM2, VM3 | 24, 13, 14 | `VM` (all three) | motor/coil power |
| VCC | 20 | `+3V3` | logic supply — 3.3 V on purpose: it sets the input threshold at ~2 V so the 595's 3.3 V outputs register cleanly. At VCC = 5 V the threshold would rise too high. No level shifters anywhere |
| GND, PGND1, PGND2 | 18, 3+4, 9+10 | `GND` | |
| STBY | 19 | `STBY` net | chip enable. Low = every output Hi-Z |
| PWMA, PWMB | 23, 15 | `+3V3` (tie high) | we don't PWM; direction is set purely by IN1/IN2 |
| AO2, BO2 | 5+6, 7+8 | **leave unconnected** | unused half of each bridge |
| AIN1, AIN2 | 21, 22 | per-chip nets (§5.9) | channel A control |
| BIN1, BIN2 | 17, 16 | per-chip nets (§5.9) | channel B control |
| AO1 | 1+2 | matrix line (table below) | drive output |
| BO1 | 11+12 | matrix line (table below) | drive output |

Decoupling per chip: **0.1 µF on VCC** and **0.1 µF on VM** (C9–C18).

**Output → matrix line map:**

| Chip | AO1 → | BO1 → |
|---|---|---|
| U1 | `R0` | `R1` |
| U2 | `R2` | `R3` |
| U3 | `R4` | `C0` |
| U4 | `C1` | `C2` |
| U5 | `C3` | `C4` |

**Truth table per line (PWM tied high):** IN1=1, IN2=0 → output sources +VM · IN1=0, IN2=1 → output sinks to GND · IN1=0, IN2=0 → Hi-Z. Firmware only ever activates one row + one column; all other 8 lines stay Hi-Z, so current has exactly one path — through the one addressed coil.

### 5.9 The 595 → TB6612 wiring map (this table IS the firmware bit map)

Label each 595 output and each driver input with the same net name and they connect. Copy this into firmware verbatim — bit 0-ish naming caveat: this is *physical* output → input; the shift order depends on the chain direction noted in §5.7.

| 595 chip | KiCad pin name (pin #) | Net | → Driver input |
|---|---|---|---|
| U6 | Q0 (15) | `U1_AIN1` | U1 AIN1 |
| U6 | Q1 (1) | `U1_AIN2` | U1 AIN2 |
| U6 | Q2 (2) | `U1_BIN1` | U1 BIN1 |
| U6 | Q3 (3) | `U1_BIN2` | U1 BIN2 |
| U6 | Q4 (4) | `U2_AIN1` | U2 AIN1 |
| U6 | Q5 (5) | `U2_AIN2` | U2 AIN2 |
| U6 | Q6 (6) | `U2_BIN1` | U2 BIN1 |
| U6 | Q7 (7) | `U2_BIN2` | U2 BIN2 |
| U7 | Q0 (15) | `U3_AIN1` | U3 AIN1 |
| U7 | Q1 (1) | `U3_AIN2` | U3 AIN2 |
| U7 | Q2 (2) | `U3_BIN1` | U3 BIN1 |
| U7 | Q3 (3) | `U3_BIN2` | U3 BIN2 |
| U7 | Q4 (4) | `U4_AIN1` | U4 AIN1 |
| U7 | Q5 (5) | `U4_AIN2` | U4 AIN2 |
| U7 | Q6 (6) | `U4_BIN1` | U4 BIN1 |
| U7 | Q7 (7) | `U4_BIN2` | U4 BIN2 |
| U8 | Q0 (15) | `U5_AIN1` | U5 AIN1 |
| U8 | Q1 (1) | `U5_AIN2` | U5 AIN2 |
| U8 | Q2 (2) | `U5_BIN1` | U5 BIN1 |
| U8 | Q3 (3) | `U5_BIN2` | U5 BIN2 |
| U8 | Q4 (4) | `TP1` | test header |
| U8 | Q5 (5) | `TP2` | test header |
| U8 | Q6 (6) | `TP3` | test header |
| U8 | Q7 (7) | `TP4` | test header |

### 5.10 Coil connectors

*What they do: the only interface to the hand-built display. The 25 coils are wired as a matrix on the 3D-printed frame; each coil bridges one row wire and one column wire, and those 10 wires land here.*

Two `Connector:Screw_Terminal_01x05` (J2, J3):

| J2 pin | Net | | J3 pin | Net |
|---|---|---|---|---|
| 1 | `R0` | | 1 | `C0` |
| 2 | `R1` | | 2 | `C1` |
| 3 | `R2` | | 3 | `C2` |
| 4 | `R3` | | 4 | `C3` |
| 5 | `R4` | | 5 | `C4` |

### 5.11 Test header

*What it does: probe points for bring-up, and escape hatches if a bodge is ever needed on the one-shot board.*

`Connector_Generic:Conn_01x08` (J4):

| Pin | Net |
|---|---|
| 1 | `+3V3` |
| 2 | `+5V` |
| 3 | `VM` |
| 4 | `GND` |
| 5–8 | `TP1`–`TP4` |

### 5.12 Mounting holes

Place 4× `Mechanical:MountingHole` (H1–H4). No electrical connection. (If you want them grounded to the frame, use `MountingHole_Pad` and wire to GND instead — plain unconnected holes are fine here.)

---

## 6. Power-on safety — verify you built this in (critical)

The board must energize **zero coils** from power-up until firmware explicitly takes control. Three independent layers should now exist in your schematic — check each:

1. **R1 10 kΩ pull-down on `STBY`** → all TB6612 outputs Hi-Z while GP5 is unconfigured, *regardless* of 595 output states. (§5.4)
2. **Logic rail comes from the Pico's 3V3OUT** → while the Pico is in reset/unpowered, the 595s and TB6612 logic aren't even powered. (§5.4)
3. **Firmware contract:** configure GPIO → shift an all-zeros (all-Hi-Z) frame into the 595s and latch it → *only then* drive GP5 high. Never raise STBY first.

Why it matters: a coil is only rated for ~1 ms pulses. One held continuously at ~0.64 A dissipates ~7 W and destroys itself in seconds.

---

## 7. ERC (Electrical Rules Check) — expect these, fix like this

Run **Inspect → Electrical Rules Checker** when done.

| ERC complaint | Fix |
|---|---|
| "Input Power pin not driven by any Output Power pins" on VM / +5V / GND / +12V | Place `power:PWR_FLAG` touching that net (§4). |
| Unconnected pin errors on AO2/BO2, Q7' of U8, Pico spare GPIOs, VBUS | Place a **no-connect flag** (`Q` key, the ×) on every intentionally unused pin. Don't just leave them bare. |
| Warnings about the Pico symbol pin types (community lib) | Inspect individually; typically benign — resolve with PWR_FLAG on +3V3 if its 3V3 pin isn't "power output". |

Target: **zero errors**. Warnings are acceptable only if you can explain each one.

---

## 8. Annotate, assign footprints, final cross-check

1. **Tools → Annotate Schematic** (if any refs are still `U?`).
2. **Tools → Assign Footprints** — every line must have a footprint. Use the table in §2.
3. Cross-check the following by clicking each net (KiCad highlights it):
   - [ ] `VM` touches: D1 cathode, C1/C2/C3 +, U9 VI, all 15 driver VM pins (3 per chip × 5), 5 VM decoupling caps, J4 pin 3
   - [ ] `+3V3` touches: Pico 36, U6/U7/U8 VCC + MR, all 5 TB6612 VCC + PWMA + PWMB, R2, 595 decoupling caps, J4 pin 1
   - [ ] `STBY` touches exactly: Pico GP5, R1, and pin 19 of all five drivers
   - [ ] `GND` touches: everything listed as GND above — and **all 8 Pico ground pins**
   - [ ] Each of `R0`–`R4`, `C0`–`C4` touches exactly **two** things: one driver output and one screw-terminal pin
   - [ ] Each of the 20 `Ux_yINz` nets touches exactly **two** things: one 595 output and one driver input
   - [ ] F1 is between the jack tip and D1 — nothing else taps `+12V_IN` or `+12V_F`
   - [ ] D2 orientation: anode at `+5V`, cathode at Pico VSYS (a reversed D2 = Pico never powers on)
   - [ ] D1 orientation: anode at fuse side, cathode at `VM` (reversed D1 = board never powers on)
   - [ ] LED orientations: current flows rail → resistor → anode → cathode → GND

---

## 9. Layout notes (for when you move to the PCB editor)

Not schematic work, but decisions the schematic reader needs to know:

- 2-layer, < 100 × 100 mm. Ground pour both sides, stitched with vias.
- **Star ground** at the jack/C1 node: the pulsing coil-return current must not flow through the logic-ground region or under the Pico.
- 0.1 µF caps physically at the pins they decouple. C1 next to the driver cluster; C2/C3 at the row's two ends.
- Trace widths: `VM` feed and `R0–R4`/`C0–C4` ≥ 0.4 mm (they carry ~0.7 A pulses); jack→fuse→D1→C1 path ≥ 0.6 mm; logic 0.2–0.25 mm.
- **Antenna keep-out:** no copper/pour/tall parts under and around the Pico's antenna end — which is the end **opposite the USB connector** (correction: the original spec said "USB end", which is wrong; the ki-lime `RaspberryPi_Pico_OptionalKeepoutRF` overlay footprint shows the exact zone). Overhang the antenna end past the board edge if possible — the overlay even marks "suggested board edge" lines for this.
- Screw terminals on the edge facing the display; silkscreen every terminal `R0…R4`, `C0…C4`.
- Silkscreen: `12V REGULATED ONLY`, `F1: T2A 5x20`, cap polarity marks, button names, LED meanings.

---

## 10. Bill of materials (updated: fuse added, RGB removed)

| Ref | Part | Qty | Notes |
|---|---|---|---|
| A1 | Raspberry Pi Pico 2 W | 1 | + 2× 1×20 female pin socket (board) + 2× 1×20 male header (Pico) |
| U1–U5 | TB6612FNG, SSOP-24 | 5 | dual H-bridge |
| U6–U8 | 74HC595 | 3 | DIP-16 (+3 sockets) or SOIC-16 |
| U9 | Recom R-78E5.0-1.0 | 1 | 12→5 V, 1 A, SIP-3 |
| J1 | Barrel jack 5.5×2.1 mm | 1 | center-positive |
| **F1** | **Fuse holder 5×20 mm + T2A slow-blow fuse** | **1 (+spare fuses)** | **new** |
| D1 | SS34 (DO-214AB) | 1 | reverse protection |
| D2 | SS14 (DO-214AC) or 1N5819 (DO-41) | 1 | 5V→VSYS |
| D3 | LED 5 mm green | 1 | power indicator |
| D4 | LED 5 mm red | 1 | activity indicator |
| J2, J3 | Screw terminal 5.08 mm 5-pos | 2 | coil matrix |
| J4 | Pin header 1×8 | 1 | test points |
| SW1–SW4 | Tactile switch 6×6 mm | 4 | |
| R1 | 10 kΩ | 1 | STBY pull-down |
| R2, R3 | 330 Ω | 2 | LED series |
| C1 | 1000 µF / 25 V electrolytic | 1 | VM bulk |
| C2, C3 | 100 µF / 25 V electrolytic | 2 | VM local |
| C4 | 10 µF ceramic | 1 | buck in |
| C5 | 22 µF ceramic | 1 | buck out |
| C6–C18 | 0.1 µF ceramic | 13 | decoupling (buy ~20) |
| H1–H4 | M3 standoff + screw | 4 | |
| — | 12 V **regulated** 2 A adapter | 1 | off-board |

Freed vs. old spec: GP11, GP12 (were RGB green/blue) are now spare GPIOs.

---

## 11. Open item carried over from the spec — measure before ordering parts

The coils are hand-wound; **measure their resistance before finalizing**. Target ≈ 18 Ω (reference Flipo coil: 18 Ω / 6 mH).

| Measured R | Action |
|---|---|
| ~12–25 Ω | Build exactly as this guide says |
| < ~10 Ω | Pulls > 1.2 A — over TB6612 rating. Add series R, shorten pulse, or switch to L298N (which then **needs external flyback diodes**) |
| > ~40 Ω | May not reach the ~300 mA minimum flip current. Rewind with fewer turns / thicker wire |

---

## 12. Quick FAQ for future readers (human or agent)

- **Why tri-state drivers instead of simple transistors?** Discs need current in *both* directions (bipolar), and unaddressed matrix lines must *float* to prevent sneak paths through neighboring coils. {source, sink, Hi-Z} per line is the minimum viable primitive.
- **Why only 10 driver channels for 25 dots?** Matrix wiring: coils bridge row×column intersections. 5+5 lines address 25 coils, one at a time.
- **Why shift registers at all — the Pico has 26 GPIOs?** 20 driver inputs + buttons + LEDs + STBY would consume nearly everything, leave no spares on a one-shot board, and the 595s make the frame update atomic via the latch.
- **Why is TB6612 VCC 3.3 V, not 5 V?** Input thresholds scale with VCC. At 3.3 V the chip's V_IH (~2 V) is cleanly met by 3.3 V logic; at 5 V it might not be. This kills any need for level shifters.
- **Why no flyback diodes?** TB6612FNG has them internally. (L298N does not — that's why the fallback plan adds them.)
- **Why a diode into VSYS instead of wiring 5 V straight in?** So USB (flashing) and the 12 V supply can be connected simultaneously without fighting or backfeeding.
- **Can the fuse go after the SS34 instead?** Put it before (jack → fuse → diode) so the fuse also protects against a reversed supply forcing the SS34 into sustained blocking/failure and any short upstream of the diode.
