# Bill of materials: rack power board

Almost everything comes from **DigiKey Ireland** (digikey.ie: EUR prices, ships to Ireland,
free delivery over the order threshold). The Pololu module comes from **EXP Tech**
(Germany, EU), so there are no customs charges and no shipping from the US. Standoffs come
from **Amazon.ie**.

* **Direct links** (marked 🔗) open the exact DigiKey product page. They were checked in
  November 2026.
* **Search links** (marked 🔎) run a DigiKey keyword search for the exact manufacturer part
  number. Use these where no product page was checked, or where the part has many
  packaging variants.
* Quantities are for one board. Spare fuses are listed separately.

| Ref | Qty | Part | Manufacturer / MPN | Notes | Link | Alt. link |
|---|---|---|---|---|---|---|
| U1 | 1 | DC-DC 1/8 brick, 36–75 V → 12 V / 25 A, 300 W | Flex **PKB4313DPI** | about €42; often backordered. 5-pin and 8-pin DOSA bricks both fit. Set JP1 to match the RC logic (see README). | [🔗 DigiKey](https://www.digikey.ie/en/products/detail/flex-power-modules/PKB4313DPI/10287605) | [🔎 Delta E48SC12025NRFH](https://www.digikey.ie/en/products/result?keywords=E48SC12025NRFH) |
| U2 | 1 | 5 V / 9 A step-down module | Pololu **D24V90F5** (#2866) | Mount on 4× M2 × 10 mm standoffs (see below). Comes with terminal blocks. EXP Tech: about €26 ex VAT + €15 delivery to Ireland (about €47 total). Opencircuit: about €50.50 incl. VAT + shipping. Fallback: DigiKey Marketplace (ships from the USA). | [EXP Tech](https://exp-tech.de/en/products/pololu-5v-9a-step-down-voltage-regulator-d24v90f5) | [Opencircuit](https://opencircuit.shop/product/pololu-5v-9a-step-down-voltage-regulator) |
| J1–J8 | 8 | PCB header, 2-pos, 5.08 mm, horizontal | Phoenix Contact **MSTBA 2,5/2-G-5,08** (1757242) | 12 A per contact | [🔎 DigiKey](https://www.digikey.ie/en/products/result?keywords=1757242) | |
| (J1–J8 plugs) | 8 | Pluggable screw terminal plug, 2-pos, 5.08 mm | Phoenix Contact **MSTB 2,5/2-ST-5,08** (1757019) | Mates with J1–J8 | [🔎 DigiKey](https://www.digikey.ie/en/products/result?keywords=1757019) | |
| J9 | 1 | 4-pin 5.08 mm "Molex" (8981-style) header, straight or right-angle | — | **On hand.** The footprint has tab holes for the right-angle version. | — | |
| (J9 plug) | 1 | 4-pos Mate-N-Lok plug housing (the standard PC "Molex" plug) | TE **1-480424-0** | Only needed if you make your own cable | [🔎 DigiKey](https://www.digikey.ie/en/products/result?keywords=1-480424-0) | |
| (J9 contacts) | 4 | Mate-N-Lok socket contact, 20–14 AWG, tin | TE **60619-4** | For the housing above | [🔎 DigiKey](https://www.digikey.ie/en/products/result?keywords=60619-4) | |
| F1–F3 | 3 | 5×20 mm PCB fuse holder, open | Schurter **0031.8201** | | [🔎 DigiKey](https://www.digikey.ie/en/products/result?keywords=0031.8201) | |
| (F1–F3 covers) | 3 | Cover for 0031.8201 (optional) | Schurter **0853.0551** | Touch protection on the 54 V fuses | [🔎 DigiKey](https://www.digikey.ie/en/products/result?keywords=0853.0551) | |
| F1 fuse | 1 | Fuse 5×20 mm, 8 A time-lag, 250 V | Littelfuse **0218008.MXP** | 54 V input | [🔗 DigiKey](https://www.digikey.ie/en/products/detail/littelfuse-inc/0218008-MXP/777606) | |
| F2, F3 fuse | 2 | Fuse 5×20 mm, 2.5 A time-lag, 250 V | Littelfuse **02182.50MXP** | 54 V outputs | [🔎 DigiKey](https://www.digikey.ie/en/products/result?keywords=02182.50MXP) | |
| F4–F8 | 5 | Mini blade (ATM) fuse holder, PCB | Keystone **3568** | | [🔎 DigiKey](https://www.digikey.ie/en/products/result?keywords=Keystone%203568) | |
| F4–F8 fuse | 5 | Mini blade (ATM) fuse, 5 A, 32 V | Littelfuse **0297005.WXNV** | Swap in 3 A (0297003.WXNV) for smaller loads | [🔗 DigiKey](https://www.digikey.ie/en/products/detail/littelfuse-inc/0297005-WXNV/146583) | |
| C1, C2 | 2 | 68 µF 100 V electrolytic, Ø10 × 20 mm, 5 mm pitch | Nichicon **UPW2A680MPD** | Low impedance, 105 °C / 5000 h | [🔗 DigiKey](https://www.digikey.ie/en/products/detail/nichicon/UPW2A680MPD/589716) | |
| C3, C4 | 2 | 2.2 µF 100 V X7R, 1210 | Murata **GRM32ER72A225KA35L** | | [🔎 DigiKey](https://www.digikey.ie/en/products/result?keywords=GRM32ER72A225KA35L) | |
| C5, C6 | 2 | 470 µF 16 V aluminium polymer, Ø8 × 9 mm, 3.5 mm pitch | Panasonic **16SEPG470M** | 8 mΩ ESR | [🔗 DigiKey](https://www.digikey.ie/en/products/detail/panasonic-industry/16SEPG470M/8020032) | [🔗 Chemi-Con APSG160ELL471MH08J](https://www.digikey.ie/en/products/detail/chemi-con/APSG160ELL471MH08J/21805635) |
| C7, C8 | 2 | 22 µF 25 V X5R, 1210 | Murata **GRM32ER61E226KE15L** | | [🔎 DigiKey](https://www.digikey.ie/en/products/result?keywords=GRM32ER61E226KE15L) | |
| D1 | 1 | TVS diode 58 V, SMB | Littelfuse **SMBJ58A** | | [🔎 DigiKey](https://www.digikey.ie/en/products/result?keywords=SMBJ58A%20Littelfuse) | |
| D2–D4 | 3 | LED, green, 0805 | Kingbright **APT2012SGC** | Any 0805 LED will do | [🔎 DigiKey](https://www.digikey.ie/en/products/result?keywords=APT2012SGC) | |
| R1 | 1 | 47 kΩ 1 %, 1206 | Yageo **RC1206FR-0747KL** | 54 V LED | [🔎 DigiKey](https://www.digikey.ie/en/products/result?keywords=RC1206FR-0747KL) | |
| R2 | 1 | 4.7 kΩ 1 %, 1206 | Yageo **RC1206FR-074K7L** | 12 V LED | [🔎 DigiKey](https://www.digikey.ie/en/products/result?keywords=RC1206FR-074K7L) | |
| R3 | 1 | 1 kΩ 1 %, 1206 | Yageo **RC1206FR-071KL** | 5 V LED | [🔎 DigiKey](https://www.digikey.ie/en/products/result?keywords=RC1206FR-071KL) | |
| — | 4 | M3 standoff, ≥ 5 mm (board to case) + screws | any | Or printed bosses in the case | [Amazon.ie](https://www.amazon.ie/s?k=M3+brass+standoff+kit) | |
| — | 4 | M2 standoff, 10 mm (Pololu) + screws | any | | [Amazon.ie](https://www.amazon.ie/s?k=M2+brass+standoff+kit) | |
| PCB | 1 | 134 × 81 mm, 2 layers, **2 oz copper**, 1.6 mm | — | Upload `rack-power-board-gerbers.zip`. | [JLCPCB](https://jlcpcb.com/) | |

## Spare fuses (recommended)

| Part | MPN | Qty | Link |
|---|---|---|---|
| 5×20 mm 8 A T | Littelfuse 0218008.MXP | 2 | [🔗 DigiKey](https://www.digikey.ie/en/products/detail/littelfuse-inc/0218008-MXP/777606) |
| 5×20 mm 2.5 A T | Littelfuse 02182.50MXP | 2 | [🔎 DigiKey](https://www.digikey.ie/en/products/result?keywords=02182.50MXP) |
| ATM 5 A | Littelfuse 0297005.WXNV | 5 | [🔗 DigiKey](https://www.digikey.ie/en/products/detail/littelfuse-inc/0297005-WXNV/146583) |
| ATM 3 A (optional, smaller 12 V loads) | Littelfuse 0297003.WXNV | 5 | [🔎 DigiKey](https://www.digikey.ie/en/products/result?keywords=0297003.WXNV) |

## Notes

* **Not recommended for new designs:** DigiKey marks the Nichicon UPW2A680MPD (C1, C2) and
  Panasonic 16SEPG470M (C5, C6) this way, but both were in stock when checked. Any
  equivalent fits: C1/C2 need 68 µF ≥ 100 V, Ø10 mm, 5 mm pitch, ≤ 20 mm tall; C5/C6 need
  470 µF ≥ 16 V polymer, Ø8 mm, 3.5 mm pitch.
* **Pololu supply:** Pololu lists the D24V90F5 as *rationed*, so check stock before ordering. EXP Tech only had a few in stock when checked. Both EXP Tech and Opencircuit ship from inside the EU. Botland's shops either ship only domestically (Poland, Germany) or sell internationally to business customers only (botland.store).
* **Check before ordering:** the brick footprint and the J9 tab holes (see README).
