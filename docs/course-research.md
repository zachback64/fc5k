# FC5K course research — September 23, 2026

## Strava access

Signed-in Global Heatmap inspected visually with the Run filter, blue palette, and 100% opacity. At the regional view, the Illinois Prairie Path has a strong, continuous bright trace; Salt Creek also has visible continuous running activity. At park scale, Wilder’s central through-path is visibly used, while its small formal-garden paths and campus interior have weaker traces than surrounding streets. This is a qualitative visual comparison, not runner counts or an absolute popularity ranking.

Reviewed views: regional center 41.892/-87.943 at zoom 13.36; Wilder/campus center 41.8965/-87.943 at zoom 15.68; Prairie Path center 41.884/-87.951 at zoom 14.68.

Map: https://www.strava.com/maps?sport=Run&style=dark&terrain=false&labels=true#14/41.892/-87.943

## Current route audit

`data/course.json` reports 4.91 km. An exact coordinate-edge comparison finds six segments traversed in opposite directions, representing approximately 72.4 m of repeated path (counting the later traversal only):

- Glos: approximately 3.6 m, shape edges 17 / 51.
- Wilder: approximately 55.3 m, edges 113–116 / 136–139, approaching and leaving the circular feature near 41.89664, -87.94423.
- Campus: approximately 13.5 m, edges 197 / 201, near 41.8959, -87.9487.

This conflicts with the homepage's “no doubling back” claim. The existing `scripts/spurs.py` reports no spurs because it checks consecutive turning angles; it misses a route that loops around a feature and returns along an earlier edge. A replacement route should check repeated edges as well as sharp turns. The published route has not been changed during this research.

## Candidate comparison

1. **Wilder Park + campus / Glos:** closest fit to the current north-of-St.-Charles concept. Official park materials confirm running/walking paths. Simplify the circular detour and campus jog before measuring a replacement 5K. The existing options file also contains a 5.01 km “big college” draft; that stored estimate has not been rerouted or validated against Strava.
2. **Illinois Prairie Path + Wild Meadows Trace / Keith A. Olson Prairie:** candidate for a longer continuous trail section. The official district guide maps the Prairie Path east–west through Elmhurst; the prairie lies north of it between Spring Road and Salt Creek. A house-start course would need a new southern connection and St. Charles crossing review. Exact 5K geometry has not been measured.
3. **Salt Creek Greenway / Maple Trail Woods:** strongest woodland candidate from official descriptions, but assess the travel distance from the existing start before selecting it for a 5K. Maple Trail Woods connects to the Greenway south of Madison Street. Do not claim it fits a home-start 5K without routing it.

Heatmap usage does not establish public access, race suitability, or December surface conditions. Check those independently after selecting a draft.

## Primary sources

- Wilder Park: https://www.epd.org/parks/wilder-park
- Wilder walking-path map: https://www.epd.org/sites/default/files/pdf/Wilder%20Park%20Trail.pdf
- District trail guide: https://www.epd.org/sites/default/files/assets/Elmhurst-Park-District-Trail-Guide.pdf
- Keith A. Olson Prairie: https://www.epd.org/parks/keith-olson-prairie
- Salt Creek Greenway: https://www.epd.org/parks/salt-creek-greenway-trail
- Maple Trail Woods: https://www.epd.org/parks/maple-trail-woods

## Measured Prairie Path draft

Valhalla pedestrian routing on September 23 produced a **4.83 km** house-start loop: Kenmore → Church → Hagans / Spring → Illinois Prairie Path east → South Street → York → Adelia → Kenmore. The two Prairie Path maneuvers total approximately **0.92 km**. This needs roughly 170 m added to approach 5 km, followed by on-foot measurement and crossing review. It crosses St. Charles on the outbound and return legs. The draft has not replaced the event course.

A western extension trial returned 8.31 km with unwanted detours around the creek corridor. It is rejected as a 5K candidate; it is retained only in `docs/trail-drafts.json` to document the routing result.

Review map: `/trails` (uses `data/trail-review.json`).

## Six-course workshop

The workshop now offers six 5,000 m alternatives, all using the same street start by the house. Distances use cumulative haversine lengths of the routed shape. The final point is interpolated on an existing routed segment, with no invented off-road connector. Short loops continue on a pedestrian-routed stretch of Kenmore to reach 5K. Out-and-backs turn at precisely 2,500 mapped metres.

| Option | Finish |
| --- | --- |
| Prairie Path west loop | 178 m north of home |
| Prairie Path east loop | 212 m north of home |
| Glos, Wilder & quad | 103 m north of home |
| Wilder & campus perimeter | 234 m south of home |
| Prairie Path out & back | Home |
| West-side out & back | Home |

The west-side out-and-back is a road-heavy comparison toward the western parks, not a woodland run. Its 2.5 km budget does not allow a substantial Salt Creek section. Shared segments and crossing tradeoffs are stated on each card. The original event route remains unchanged.

`python3 scripts/course_workshop.py` rebuilds `data/course-workshop.json` from the stored route samples and refreshed Kenmore continuation routing. `tests/test_courses.py` verifies 5,000 m totals, common starts, nearby finishes, kilometre markers, and 2,500 m turnarounds. These numerical tests do not certify the distance on the ground.


## Continuous-running revision — 2026-09-23

Supersedes the earlier six-option descriptions above. User requested separate crossings of busy roads, avoiding major junctions such as York / St. Charles. All six final polylines now clear a 100 m buffer around that junction (41.890296, -87.940064); the test checks whole segments, not only vertices.

- West Prairie loop uses Marion / Kenilworth / Church outbound, Spring to the trail, then the South Street connector / Kenilworth / Adelia homeward. Finishes about 128 m south of the house.
- East Prairie option is now an out-and-back via Kenilworth, avoiding York entirely.
- West Prairie out-and-back uses Kenilworth, crossing York separately at the trail.
- Glos/Wilder, campus, and west-side options remain north of St. Charles.
- Three out-and-backs now finish at the house; all six remain 5,000 m cumulative mapped geometry.

Kenilworth connector and road geometry checked against the OpenStreetMap API map extract (bbox -87.952,41.883,-87.928,41.895), with pedestrian routes from Valhalla. Sources are retained in option-samples.json. Amber map dots identify selected crossings of York, St. Charles, and Spring; repeated out-and-back crossings share a dot. These are not a comprehensive inventory of minor-road crossings or verified signal timing. Separate crossings may still require waiting.
