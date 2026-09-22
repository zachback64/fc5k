#!/usr/bin/env python3
"""Route the FC5K course on real streets/paths and write data/course.json.

Course = out to Wilder Park, one lap around the park and Elmhurst University,
back the same way. Edit the waypoint lists and run: python3 scripts/course.py
Routing: Valhalla public server, pedestrian costing, OpenStreetMap data.
"""
import json
from pathlib import Path
from valhalla import route

START = (41.893837, -87.935259)   # 238 S Kenmore (Census geocoder, house-level)
PARK = (41.89451, -87.94259)        # Wilder Park SE corner, Church & Cottage Hill

OUT = [START, (41.89441, -87.93998), PARK]   # Church St, York, Elmwood Terrace, Cottage Hill
LAP = [PARK,                        # counter-clockwise, every turn is a left
       (41.89529, -87.94398),       # into the park, up the middle path
       (41.89758, -87.94475),       # out the park's west side at Prospect
       (41.89794, -87.94905),       # left on Alexander, west along the college
       (41.89778, -87.95207),       # left on Fairfield
       (41.89425, -87.94948),       # left on Elm Park
       (41.89442, -87.94488),       # Elm Park becomes Church at Prospect
       PARK]

if __name__ == "__main__":
    k1, s1, sh1, c1 = route(OUT)
    k2, s2, sh2, c2 = route(LAP)
    k3, s3, sh3, c3 = k1, s1, list(reversed(sh1)), []   # back the way you came
    km = k1 + k2 + k3
    shape = sh1 + sh2[1:] + sh3[1:]
    out = {"km": round(km, 2), "miles": round(km * 0.621371, 2), "start": START, "park": PARK,
           "legs": [{"name": "Out", "km": round(k1, 2), "cues": c1, "n": len(sh1)},
                    {"name": "Lap", "km": round(k2, 2), "cues": c2, "n": len(sh2) - 1},
                    {"name": "Back", "km": round(k3, 2), "cues": c3, "n": len(sh3) - 1}],
           "shape": [[round(a, 6), round(b, 6)] for a, b in shape]}
    Path(__file__).resolve().parent.parent.joinpath("data", "course.json").write_text(json.dumps(out))
    from spurs import spurs
    bad = spurs(shape)
    if bad: print("WARNING out-and-back spurs at", bad)
    print(f"{km:.2f} km ({km*0.621371:.2f} mi)  out {k1:.2f}  lap {k2:.2f}  back {k3:.2f}")
    for leg in out["legs"]:
        print("--", leg["name"]); [print("  ", c["km"], c["text"]) for c in leg["cues"]]
