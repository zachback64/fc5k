#!/usr/bin/env python3
"""Route the FC5K course on real streets/paths and write data/course.json.

Course = out to Wilder Park, one lap around the park and Elmhurst University,
back the same way. Edit the waypoint lists and run: python3 scripts/course.py
Routing: Valhalla public server, pedestrian costing, OpenStreetMap data.
"""
import json
from pathlib import Path
from valhalla import route

START = (41.8944962, -87.9351743)   # 238 S Kenmore
PARK = (41.89451, -87.94259)        # Wilder Park, SE corner (Church & Cottage Hill)

OUT = [START, (41.89441, -87.93998), PARK]   # Church St, York, Elmwood Terrace, Cottage Hill
LAP = [PARK,
       (41.8961, -87.94257),        # park path, east side, heading north
       (41.89841, -87.94255),       # park NE
       (41.89869, -87.94421),       # across the top of the park
       (41.89808, -87.94493),       # into Elmhurst University
       (41.89794, -87.94905),       # along the north edge of campus
       (41.8968, -87.9517),         # around the football field
       (41.8952, -87.9470),         # back east
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
    print(f"{km:.2f} km ({km*0.621371:.2f} mi)  out {k1:.2f}  lap {k2:.2f}  back {k3:.2f}")
    for leg in out["legs"]:
        print("--", leg["name"]); [print("  ", c["km"], c["text"]) for c in leg["cues"]]
