#!/usr/bin/env python3
"""Route the FC5K course on real streets and park paths; write data/course.json.

One loop, no doubling back: Kenmore -> Glos Memorial Park -> across York ->
Wilder Park top to bottom on the main path -> the college quad -> Wilder's
southeast garden path -> Church -> home. Edit LEGS and run:
    python3 scripts/course.py
Routing: Valhalla public server, pedestrian costing, OpenStreetMap data.
Each leg is <= 10 waypoints (server limit); legs are joined end to end.
"""
import json
from pathlib import Path
from valhalla import route
from spurs import spurs

START = (41.893837, -87.935259)   # 238 S Kenmore (Census geocoder, house-level)

LEGS = [
    ("Kenmore to Glos Memorial Park", [
        START,
        (41.8971, -87.9352),         # Kenmore & Marion
        (41.8976, -87.9375),         # into Glos on the diagonal path
        (41.89815, -87.93821),       # Glos, middle
        (41.8985, -87.9395),         # out the west side to York & Adelaide
    ]),
    ("Across York into Wilder Park", [
        (41.8985, -87.9395),
        (41.8985, -87.9425),         # Adelaide & Cottage Hill
        (41.89756, -87.94255),       # Wilder Park, northeast entrance
    ]),
    ("Down the middle of Wilder Park", [
        (41.89756, -87.94255),
        (41.89664, -87.94423),
        (41.8971, -87.94371),        # main path
        (41.89755, -87.9444),
        (41.89758, -87.94475),       # out at Prospect
    ]),
    ("Through the college", [
        (41.89758, -87.94475),
        (41.8973, -87.94598),        # Alumni Circle
        (41.8962, -87.9474),         # College Mall, the quad
        (41.89597, -87.94877),       # west end of the quad walkway
        (41.89536, -87.94882),       # south along the campus west walkway
        (41.89489, -87.94579),       # east along the campus south walkway
        (41.89442, -87.94488),       # Prospect & Church
    ]),
    ("Wilder Park's garden path", [
        (41.89442, -87.94488),
        (41.89463, -87.9445),        # southwest corner path
        (41.89471, -87.9442),
        (41.89465, -87.944),
        (41.89452, -87.94379),
        (41.89452, -87.94339),
        (41.89451, -87.94259),       # out at Church & Cottage Hill
    ]),
    ("Church, York, Adelia, home", [
        (41.89451, -87.94259),
        (41.89441, -87.93998),       # Church & York
        (41.89371, -87.93998),       # York & Adelia
        START,
    ]),
]

if __name__ == "__main__":
    total = 0.0; shape = []; legs = []
    for name, pts in LEGS:
        km, streets, sh, cues = route(pts)
        total += km
        shape += sh if not shape else sh[1:]
        legs.append({"name": name, "km": round(km, 2), "streets": streets, "n": len(sh)})
        print(f"{km:5.2f} km  {name}  ({' > '.join(streets) or 'paths'})")
    bad = spurs(shape)
    if bad:
        print("WARNING out-and-back spurs at", bad)
    out = {"km": round(total, 2), "miles": round(total * 0.621371, 2), "start": START,
           "park": (41.89756, -87.94255), "legs": legs,
           "shape": [[round(a, 6), round(b, 6)] for a, b in shape]}
    Path(__file__).resolve().parent.parent.joinpath("data", "course.json").write_text(json.dumps(out))
    print(f"TOTAL {total:.2f} km ({total*0.621371:.2f} mi)")
