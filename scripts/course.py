#!/usr/bin/env python3
"""Route the FC5K course on real streets and write data/course.json.

Edit WAYPOINTS (lat, lon) and run: python3 scripts/course.py
Routing: Valhalla public server, pedestrian costing, OSM data.
"""
import json
from pathlib import Path
from valhalla import route

S = (41.8944962, -87.9351743)          # 238 S Kenmore
WAYPOINTS = [
    S,
    (41.89441, -87.93998),              # Church & York
    (41.8944, -87.9448),                # Cottage Hill & Church (Wilder Park SW corner)
    (41.8960, -87.94475),               # park path, west side
    (41.89869, -87.94421),              # park north crossing
    (41.89808, -87.94493),              # into Elmhurst University
    (41.89794, -87.94905),              # campus north path, west end
    (41.8995, -87.9490),                # Alexander / Myrtle
    (41.8999, -87.9400),                # Park Ave & York
    (41.9008, -87.9400),                # York, north of the tracks (downtown)
    (41.8996, -87.9352),                # East Park Ave & Kenmore
    S,
]

if __name__ == "__main__":
    km, streets, shape = route(WAYPOINTS)
    out = {"km": round(km, 2), "miles": round(km * 0.621371, 2), "streets": streets,
           "start": S, "shape": [[round(a, 6), round(b, 6)] for a, b in shape]}
    Path(__file__).resolve().parent.parent.joinpath("data", "course.json").write_text(json.dumps(out))
    print(f"{km:.2f} km ({km*0.621371:.2f} mi)", " > ".join(streets))
