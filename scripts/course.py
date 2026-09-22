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
PARK = (41.895356, -87.942581)  # Wilder Park east path, where Cottage Hill meets it

OUT = [START, (41.89441, -87.93998), PARK]   # Church St, York, Elmwood Terrace, Cottage Hill
LAP = [PARK,
       (41.89841, -87.94255),       # up the park's east path to the NE corner
       (41.89803, -87.94486),       # across the top to Alexander & Prospect
       (41.89794, -87.94905),       # west on Alexander past the college
       (41.89778, -87.95207),       # Fairfield Ave, turn south
       (41.89425, -87.94948),       # Elm Park Ave, turn east
       (41.89442, -87.94488),       # Prospect & Church, park SW corner
       PARK]

if __name__ == "__main__":
    k1, s1, sh1, c1 = route(OUT)
    k2, s2, sh2, c2 = route(LAP)
    k3, s3, sh3, c3 = route(list(reversed(OUT)))
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
