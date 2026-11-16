# Bill of materials: rack power board

Almost everything comes from **DigiKey Ireland** (digikey.ie: EUR prices, ships to Ireland,
free delivery over the order threshold). The Pololu module is also ordered from DigiKey, via
DigiKey Marketplace (Pololu ships it from the USA). Connectors, cables, standoffs and inserts marked *on hand* are already in stock.

* **Direct links** (marked 🔗) open the exact DigiKey product page. They were checked in
  November 2026.
* **Search links** (marked 🔎) run a DigiKey keyword search for the exact manufacturer part
  number. Use these where no product page was checked, or where the part has many
  packaging variants.
* Quantities are for one board. Spare fuses are listed separately.

| Ref | Qty | Part | Manufacturer / MPN | Notes | Link | Alt. link |
|---|---|---|---|---|---|---|
| U1 | 1 | DC-DC 1/8 brick, 36–75 V → 12 V / 25 A, 300 W | Murata **DVE0125V2NBC** | About €61 ex VAT, in stock at DigiKey (non-cancelable/non-returnable). Industry-standard 5-pin eighth brick (no PMBus, no sense/trim): pin rows 2.000" apart, outer pins 0.600" apart, matching the footprint. Baseplate, 13.2 mm tall. Pin functions match by position (checked against the Murata top view): 1 +Vin, 2 RC, 4 −Vin, 16 +Vout, 5 −Vout correspond to board pins 1, 2, 3, 8, 4. "N" = negative on/off logic: **bridge JP1**. Alternatives (backordered Nov 2026): Flex PKB4313DPI (DigiKey, about €42), Delta E48SC12025NRFH (Mouser). | [🔗 DigiKey](https://www.digikey.ie/en/products/detail/murata-power-solutions-inc/DVE0125V2NBC/5980025) | [🔗 Flex PKB4313DPI (DigiKey)](https://www.digikey.ie/en/products/detail/flex-power-modules/PKB4313DPI/10287605) |
| U2 | 1 | 5 V / 9 A step-down module | Pololu **D24V90F5** (#2866) | Mount on 4× M2 × 10 mm standoffs (see below). Comes with terminal blocks. Sold through DigiKey Marketplace (shipped by Pololu from the USA); covered by DigiKey's free delivery over €50 (checked in the cart, Nov 2026). EU alternative: Opencircuit, about €50.50 + €15.95 delivery to Ireland (free above €250). | [🔎 DigiKey (Marketplace)](https://www.digikey.ie/en/products/result?keywords=Pololu%202866) | [Opencircuit](https://opencircuit.shop/product/pololu-5v-9a-step-down-voltage-regulator) |
| J1–J8 | 8 | PCB header, 2-pos, 3.96 mm, straight | JST **B2P-VH** | **On hand.** 10 A per contact | — | |
| (J1–J8 plugs) | 8 | Crimp housing, 2-pos, 3.96 mm + contacts | JST **VHR-2N** + SVH contacts | **On hand.** Use 0.75–1.25 mm² wire (AWG 18–16) for the 5 A / 6 A outputs | — | |
| J9 | 1 | 4-pin 5.08 mm "Molex" (8981-style) header, straight or right-angle | — | **On hand.** The footprint has tab holes for the right-angle version. | — | |
| (J9 plug) | 1 | 4-pos Mate-N-Lok plug + cable | — | **On hand** | — | |
| F1–F3 | 3 | 5×20 mm PCB fuse holder, open | Schurter **0031.8201** | | [🔎 DigiKey](https://www.digikey.ie/en/products/result?keywords=0031.8201) | |
| (F1–F3 covers) | 3 | Cover for 0031.8201 (optional) | Schurter **0853.0551** | Touch protection on the 54 V fuses | [🔎 DigiKey](https://www.digikey.ie/en/products/result?keywords=0853.0551) | |
| F1 fuse | 1 | Fuse 5×20 mm, 8 A time-lag, 250 V | Littelfuse **0218008.MXP** | 54 V input | [🔗 DigiKey](https://www.digikey.ie/en/products/detail/littelfuse-inc/0218008-MXP/777606) | |
| F2, F3 fuse | 2 | Fuse 5×20 mm, 2.5 A time-lag, 250 V | Littelfuse **021802.5MXP** | 54 V outputs | [🔗 DigiKey](https://www.digikey.ie/en/products/detail/littelfuse-inc/021802-5MXP/777614) | [🔎 021502.5MXP (ceramic, DC-rated)](https://www.digikey.ie/en/products/result?keywords=021502.5MXP) |
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
| — | 4 | M3 mounting (board to case) | printed bosses + M3 heat-set inserts | **On hand** | — | |
| — | 4 | M2 standoff, 10 mm (Pololu) + screws | — | **On hand** | — | |
| PCB | 1 | 134 × 78.5 mm, 2 layers, **2 oz copper**, 1.6 mm | — | Upload `rack-power-board-gerbers.zip`. | [JLCPCB](https://jlcpcb.com/) | |

## Spare fuses (recommended)

| Part | MPN | Qty | Link |
|---|---|---|---|
| 5×20 mm 8 A T | Littelfuse 0218008.MXP | 2 | [🔗 DigiKey](https://www.digikey.ie/en/products/detail/littelfuse-inc/0218008-MXP/777606) |
| 5×20 mm 2.5 A T | Littelfuse 021802.5MXP | 2 | [🔗 DigiKey](https://www.digikey.ie/en/products/detail/littelfuse-inc/021802-5MXP/777614) |
| ATM 5 A | Littelfuse 0297005.WXNV | 5 | [🔗 DigiKey](https://www.digikey.ie/en/products/detail/littelfuse-inc/0297005-WXNV/146583) |
| ATM 3 A (optional, smaller 12 V loads) | Littelfuse 0297003.WXNV | 5 | [🔎 DigiKey](https://www.digikey.ie/en/products/result?keywords=0297003.WXNV) |

## Notes

* **Not recommended for new designs:** DigiKey marks the Nichicon UPW2A680MPD (C1, C2) and
  Panasonic 16SEPG470M (C5, C6) this way, but both were in stock when checked. Any
  equivalent fits: C1/C2 need 68 µF ≥ 100 V, Ø10 mm, 5 mm pitch, ≤ 20 mm tall; C5/C6 need
  470 µF ≥ 16 V polymer, Ø8 mm, 3.5 mm pitch.
* **Pololu supply:** Pololu lists the D24V90F5 as *rationed*, so check stock before ordering. EU sellers checked: EXP Tech (Germany) was backorder-only, and Opencircuit (Netherlands) charges €15.95 delivery to Ireland. That makes DigiKey the cheapest overall. Botland's shops either ship only domestically (Poland, Germany) or sell internationally to business customers only (botland.store).
* **Check before ordering:** the brick footprint and the J9 tab holes (see README).
