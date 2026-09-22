#!/usr/bin/env python3
"""Route several candidate courses and write data/options.json for options.html."""
import json
from pathlib import Path
from valhalla import route
from spurs import spurs

S = (41.893837, -87.935259)          # 238 S Kenmore
# Glos Memorial Park: OSM's path isn't joined to Marion St, so the park leg is
# spliced in by hand: route to Marion & Arlington, walk the park path S->N
# (data/glos_path.json), then route on from the Park Ave gate.
GLOS_PATH = [tuple(p) for p in json.load(open(Path(__file__).resolve().parent.parent / "data" / "glos_path.json"))]
TO_GLOS = [S, (41.8971, -87.9352), (41.89705, -87.93675)]   # Kenmore, Marion, to Marion & Arlington (Glos's SE corner)
FROM_GLOS = [(41.89905, -87.94000), (41.89851, -87.94000), (41.8985, -87.9425), (41.89756, -87.94255)]  # Park Ave gate, York, Adelaide, Cottage Hill
GLOS = ("manual", GLOS_PATH + [(41.89935, -87.93845), (41.89930, -87.93990)])   # then west along Park Ave to York
YORK_TO_WILDER = FROM_GLOS
WILDER_MID = [(41.89756, -87.94255), (41.89664, -87.94423), (41.8971, -87.94371), (41.89755, -87.9444), (41.89758, -87.94475)]
QUAD = [(41.89758, -87.94475), (41.8973, -87.94598), (41.8962, -87.9474), (41.89597, -87.94877), (41.89536, -87.94882), (41.89489, -87.94579), (41.89442, -87.94488)]
PERIM = [(41.89758, -87.94475), (41.89803, -87.94486), (41.89794, -87.94905), (41.89778, -87.95207), (41.89425, -87.94948), (41.89442, -87.94488)]
GARDEN = [(41.89442, -87.94488), (41.89463, -87.9445), (41.89471, -87.9442), (41.89465, -87.944), (41.89452, -87.94379), (41.89452, -87.94339), (41.89451, -87.94259)]
HOME = [(41.89451, -87.94259), (41.89441, -87.93998), (41.89371, -87.93998), S]
ENT = (41.895356, -87.942581)
STEM = [S, (41.89441, -87.93998), ENT]
LAP = [ENT, (41.89561, -87.94395), (41.89659, -87.94364), (41.89755, -87.9444), (41.89758, -87.94475),
       (41.89794, -87.94905), (41.89778, -87.95207), (41.89425, -87.94948), (41.89442, -87.94488), ENT]

OPTIONS = {
    "A. Green loop": {"blurb": "Glos, down the middle of Wilder, the college quad, Wilder's garden path, home.",
                      "legs": [TO_GLOS, GLOS, YORK_TO_WILDER, WILDER_MID, QUAD, GARDEN, HOME]},
    "B. Green loop, big college": {"blurb": "Same, but around the whole college (Alexander, Fairfield, Elm Park) instead of the quad.",
                      "legs": [TO_GLOS, GLOS, YORK_TO_WILDER, WILDER_MID, PERIM, GARDEN, HOME]},
    "C. Two parks only": {"blurb": "Glos, down the middle of Wilder, garden path, home. Short.",
                      "legs": [TO_GLOS, GLOS, YORK_TO_WILDER, WILDER_MID, [(41.89758, -87.94475), (41.89646, -87.94475), (41.89452, -87.94478)], GARDEN[1:], HOME]},
    "D. Lollipop": {"blurb": "Church to Wilder, one lap through the park and around the college, back the same way.",
                      "legs": [STEM, LAP, list(reversed(STEM))]},
}

if __name__ == "__main__":
    out = {}
    for name, o in OPTIONS.items():
        total = 0.0; shape = []
        for pts in o["legs"]:
            if isinstance(pts, tuple) and pts[0] == "manual":
                sh = pts[1]; km = sum(((a[0]-b[0])**2*12321 + (a[1]-b[1])**2*6851)**0.5 for a, b in zip(sh, sh[1:]))
            else:
                km, streets, sh, cues = route(pts)
            total += km
            shape += sh if not shape else sh[1:]
        bad = spurs(shape)
        out[name] = {"km": round(total, 2), "blurb": o["blurb"], "spurs": [[b[1], b[2]] for b in bad],
                     "shape": [[round(a, 6), round(b, 6)] for a, b in shape]}
        print(f"{name}: {total:.2f} km, {len(bad)} spurs {bad}")
    Path(__file__).resolve().parent.parent.joinpath("data", "options.json").write_text(json.dumps(out))
