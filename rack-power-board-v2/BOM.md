# Bill of materials: rack power board v2

Same sourcing as [v1](../rack-power-board/BOM.md): almost everything from **DigiKey Ireland**
(digikey.ie, EUR prices, free delivery over the order threshold), the Pololu from
**Opencircuit** (EU). Parts marked *on hand* are already in stock.

* **Direct links** (🔗) open the exact DigiKey product page (checked November 2026).
* **Search links** (🔎) run a DigiKey keyword search for the exact manufacturer part number.
* Quantities are for one board. Spare fuses are listed separately.
* The supplies themselves (LOP-300-54 and LOP-200-12 / LOP-300-12) are not listed here.

| Ref | Qty | Part | Manufacturer / MPN | Notes | Link | Alt. link |
|---|---|---|---|---|---|---|
| U2 | 1 | 5 V / 9 A step-down module | Pololu **D24V90F5** (#2866) | Same as v1. Mount on 4× M2 × 10 mm standoffs. Opencircuit: about €50.50 incl. VAT + €15.95 delivery to Ireland. | [Opencircuit](https://opencircuit.shop/product/pololu-5v-9a-step-down-voltage-regulator) | [Pololu direct](https://www.pololu.com/product/2866) |
| J1, J10 | 2 | PCB header, 6-pos, 3.96 mm, straight | JST **B6P-VH** | 54 V and 12 V inputs, 10 A per contact | [🔎 DigiKey](https://www.digikey.ie/en/products/result?keywords=B6P-VH) | |
| (J1, J10 plugs) | 2 | Crimp housing, 6-pos, 3.96 mm | JST **VHR-6N** | | [🔎 DigiKey](https://www.digikey.ie/en/products/result?keywords=VHR-6N) | |
| (J1, J10 contacts) | 12 (+4 spare) | Crimp contact, AWG 18–16 | JST **SVH-41T-P1.1** | Use 1.25 mm² (AWG 16) wire | [🔎 DigiKey](https://www.digikey.ie/en/products/result?keywords=SVH-41T-P1.1) | |
| J2–J8 | 7 | PCB header, 2-pos, 3.96 mm, straight | JST **B2P-VH** | **On hand** (8 on hand, one spare) | — | |
| (J2–J8 plugs) | 7 | Crimp housing, 2-pos + contacts | JST **VHR-2N** + SVH contacts | **On hand** | — | |
| J9 | 1 | 4-pin 5.08 mm "Molex" (8981-style) header, straight or right-angle | — | **On hand.** Tab holes for the right-angle version. | — | |
| (J9 plug) | 1 | 4-pos Mate-N-Lok plug + cable | — | **On hand** | — | |
| F2, F3 | 2 | 5×20 mm PCB fuse holder, open | Schurter **0031.8201** | | [🔎 DigiKey](https://www.digikey.ie/en/products/result?keywords=0031.8201) | |
| (F2, F3 covers) | 2 | Cover for 0031.8201 (optional) | Schurter **0853.0551** | Touch protection on the 54 V fuses | [🔎 DigiKey](https://www.digikey.ie/en/products/result?keywords=0853.0551) | |
| F2, F3 fuse | 2 | Fuse 5×20 mm, 2.5 A time-lag, 250 V | Littelfuse **021802.5MXP** | 54 V outputs | [🔗 DigiKey](https://www.digikey.ie/en/products/detail/littelfuse-inc/021802-5MXP/777614) | [🔎 021502.5MXP (ceramic, DC-rated)](https://www.digikey.ie/en/products/result?keywords=021502.5MXP) |
| F4–F8 | 5 | Mini blade (ATM) fuse holder, PCB | Keystone **3568** | | [🔎 DigiKey](https://www.digikey.ie/en/products/result?keywords=Keystone%203568) | |
| F4–F8 fuse | 5 | Mini blade (ATM) fuse, 5 A, 32 V | Littelfuse **0297005.WXNV** | Swap in 3 A (0297003.WXNV) for smaller loads | [🔗 DigiKey](https://www.digikey.ie/en/products/detail/littelfuse-inc/0297005-WXNV/146583) | |
| C5, C6 | 2 | 470 µF 16 V aluminium polymer, Ø8 × 9 mm, 3.5 mm pitch | Panasonic **16SEPG470M** | 12 V input bulk capacitance | [🔗 DigiKey](https://www.digikey.ie/en/products/detail/panasonic-industry/16SEPG470M/8020032) | [🔗 Chemi-Con APSG160ELL471MH08J](https://www.digikey.ie/en/products/detail/chemi-con/APSG160ELL471MH08J/21805635) |
| D2–D4 | 3 | Pin header, 1×2, 2.54 mm, straight (LED connector) | Sullins **PREC002SAAN-RC** | Or snap 2-pin pieces off any 2.54 mm header strip. Pin 1 (`+`) = LED anode, pin 2 = GND. | [🔎 DigiKey](https://www.digikey.ie/en/products/result?keywords=PREC002SAAN-RC) | |
| (case LEDs) | 3 | 3 mm or 5 mm LED + female Dupont lead | — | User-supplied. Plain LEDs, no built-in resistor. | — | |
| R1 | 1 | 47 kΩ 1 %, 1206 | Yageo **RC1206FR-0747KL** | 54 V LED (about 1.1 mA) | [🔎 DigiKey](https://www.digikey.ie/en/products/result?keywords=RC1206FR-0747KL) | |
| R2 | 1 | 4.7 kΩ 1 %, 1206 | Yageo **RC1206FR-074K7L** | 12 V LED (about 2 mA) | [🔎 DigiKey](https://www.digikey.ie/en/products/result?keywords=RC1206FR-074K7L) | |
| R3 | 1 | 1 kΩ 1 %, 1206 | Yageo **RC1206FR-071KL** | 5 V LED (about 3 mA) | [🔎 DigiKey](https://www.digikey.ie/en/products/result?keywords=RC1206FR-071KL) | |
| JP2 | — | Solder jumper (on the PCB) | — | Open by default; bridge to tie GND54 to GND | — | |
| — | 4 | M3 mounting (board to case) | printed bosses + M3 heat-set inserts | **On hand** | — | |
| — | 4 | M2 standoff, 10 mm (Pololu) + screws | — | **On hand** | — | |
| PCB | 1 | 83.2 × 80 mm, 2 layers, **2 oz copper**, 1.6 mm | — | Upload `rack-power-board-v2-gerbers.zip`. | [JLCPCB](https://jlcpcb.com/) | |

**Not needed on v2** (compared with v1): U1 (12 V brick), C1–C4, C7, C8, D1 (TVS), F1 and
its 8 A fuse, JP1.

## Spare fuses (recommended)

| Part | MPN | Qty | Link |
|---|---|---|---|
| 5×20 mm 2.5 A T | Littelfuse 021802.5MXP | 2 | [🔗 DigiKey](https://www.digikey.ie/en/products/detail/littelfuse-inc/021802-5MXP/777614) |
| ATM 5 A | Littelfuse 0297005.WXNV | 5 | [🔗 DigiKey](https://www.digikey.ie/en/products/detail/littelfuse-inc/0297005-WXNV/146583) |
| ATM 3 A (optional, smaller 12 V loads) | Littelfuse 0297003.WXNV | 5 | [🔎 DigiKey](https://www.digikey.ie/en/products/result?keywords=0297003.WXNV) |
