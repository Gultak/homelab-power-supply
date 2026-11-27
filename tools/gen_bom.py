#!/usr/bin/env python3
"""Writes BOM.md and digikey-bom.csv from tools/bom_data.py.
Run from anywhere: python3 tools/gen_bom.py (after editing bom_data.py; keep the parts sheets in sync)."""
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path[:0] = [str(HERE), str(ROOT / "tools" / "agent-tools")]   # git submodule Gultak/agent-tools
from bom_data import PARTS
from bom.bomgen import OrderList, digikey_link, eur, md_table

HEAD = """# Bill of materials: rack power board

Quantities are for one board and include spare fuses. Prices are DigiKey Ireland line totals in EUR
including VAT, as checked in November 2026.

| Status | Meaning |
|---|---|
| 🛒 | Order from DigiKey Ireland |
| 🏠 | At hand |
| 🚚 | Ordered elsewhere, on the way |
| 🟩 | PCB, ordered from JLCPCB |

## Parts list
"""

NOTES = """
## Notes

* **DigiKey upload:** [`digikey-bom.csv`](digikey-bom.csv) has the 🛒 lines with quantities and DigiKey part numbers, ready for the DigiKey cart or BOM Manager upload.
* **Use the cut-tape DigiKey numbers (`…CT-ND`)**, not tape and reel (`…TR-ND`). Tape and reel is sold only as full
  reels (4,000 pieces for the 2512).
* **R1 is a 1 W 2512.** A 1206 at that value would overheat: R1 dissipates about 0.53 W.
* **LEDs:** use the plain SSI-LXMP059ID, not the SSI-LXMP059ID5V150 variant, which has a resistor built in. Solder half
  a female–female Dupont lead to each LED.
* **J9:** fit one of the two headers, right-angle or vertical. The board has holes for both.
* **Delivery:** DigiKey Ireland delivers free from €92.25 inc. VAT; below that, delivery is about €25.
"""

total = sum(p[8] for p in PARTS if p[0] == "🛒")
rows = [[st, ref, qty, part, man, mpn, digikey_link(dk, url) if dk else "", eur(e)]
        for st, ref, qty, part, man, mpn, dk, url, e, _order in PARTS]
rows.append(["", "**Total**", "", "**DigiKey order (🛒)**", "", "", "", f"**{total:.2f}**"])
table = md_table(["Status", "Ref", "Qty", "Part", "Manufacturer", "Part number", "DigiKey part #", "€ inc. VAT"], rows, compact_empty=True)
(ROOT / "BOM.md").write_text(HEAD + "\n" + table + "\n" + NOTES)

order = OrderList(columns=("qty", "dk", "mpn", "man", "ref"), headers={"dk": "DigiKey Part Number"},
                  lineterminator="\n")
for st, ref, qty, part, man, mpn, dk, url, e, o in PARTS:
    if st == "🛒":
        order.add(o[0], dk, man, mpn.split(" ")[0], o[1])
order.write(ROOT / "digikey-bom.csv")
print(f"BOM.md + digikey-bom.csv: {len(PARTS)} parts, DigiKey €{total:.2f}")
