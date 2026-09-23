#!/usr/bin/env python3
"""Build seven draft 5,000 m courses from routed source geometry.

Distances are cumulative haversine lengths, not race certification. Only trim
along routed segments; never add a straight connector to make a route fit.
Run from the repository root after docs/option-samples.json has been generated.
"""
import json
import math
from pathlib import Path
from valhalla import route

ROOT = Path(__file__).resolve().parent.parent
RADIUS = 6371008.8


def distance(a, b):
    lat1, lon1 = map(math.radians, a)
    lat2, lon2 = map(math.radians, b)
    h = math.sin((lat2-lat1)/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin((lon2-lon1)/2)**2
    return 2*RADIUS*math.asin(min(1, math.sqrt(h)))


def length(shape):
    return sum(distance(a,b) for a,b in zip(shape,shape[1:]))


def trim(shape, meters):
    result = [list(shape[0])]
    remaining = meters
    for a,b in zip(shape,shape[1:]):
        segment = distance(a,b)
        if segment < remaining:
            result.append(list(b)); remaining -= segment
        else:
            lo,hi=0.,1.
            for _ in range(50):
                t=(lo+hi)/2
                point=[a[0]+t*(b[0]-a[0]),a[1]+t*(b[1]-a[1])]
                if distance(a,point)<remaining:lo=t
                else:hi=t
            result.append(point)
            return result
    raise ValueError('Source geometry is shorter than the requested distance')


def reverse_length(shape):
    seen=set(); repeated=0.
    for a,b in zip(shape,shape[1:]):
        a,b=tuple(a),tuple(b)
        if (b,a) in seen:repeated+=distance(a,b)
        seen.add((a,b))
    return repeated


YORK_ST_CHARLES = [41.890296, -87.940064]

def segment_distance(point, a, b):
    # Local tangent-plane projection, adequate for this small junction buffer.
    scale = math.cos(math.radians(point[0]))
    ax, ay = (a[1]-point[1])*scale, a[0]-point[0]
    bx, by = (b[1]-point[1])*scale, b[0]-point[0]
    dx, dy = bx-ax, by-ay
    t = max(0, min(1, -(ax*dx+ay*dy)/(dx*dx+dy*dy))) if dx*dx+dy*dy else 0
    return distance(point, [a[0]+t*(b[0]-a[0]), a[1]+t*(b[1]-a[1])])

def crossing(name, lat, lon):
    return {'name':name, 'point':[lat,lon]}

KENILWORTH = crossing('St. Charles at Kenilworth',41.890262,-87.938453)
YORK_PATH = crossing('York at the Prairie Path',41.884497,-87.939999)
SPRING_PATH = crossing('Spring at the Prairie Path',41.885245,-87.94965)
YORK_CHURCH = crossing('York at Church',41.894496,-87.940055)
CROSSINGS = {
    'orchard-loop':[crossing('St. Charles at Hill',41.8901395,-87.9344337),YORK_PATH,SPRING_PATH,crossing('St. Charles at Spring',41.890321,-87.949673),YORK_CHURCH],
    'prairie-west':[YORK_CHURCH,crossing('St. Charles at Spring',41.890321,-87.949673),YORK_PATH,KENILWORTH],
    'prairie-east':[KENILWORTH],
    'green':[crossing('York near Adelaide',41.89862,-87.94006),crossing('York at Adelia',41.892303,-87.940068)],
    'campus':[crossing('York near Adelaide',41.898475,-87.94007),YORK_CHURCH],
    'prairie-return':[KENILWORTH,YORK_PATH,SPRING_PATH],
    'west-return':[YORK_CHURCH],
}


def build():
    sources=json.loads((ROOT/'docs/option-samples.json').read_text())
    current=json.loads((ROOT/'data/course.json').read_text())
    west=json.loads((ROOT/'docs/trail-drafts.json').read_text())['Prairie Path via Spring']
    home=current['shape'][0]
    extensions={}
    for direction,end in [('north',(41.8971,-87.93515)),('south',(41.8909,-87.9352))]:
        extensions[direction]=route([home,end])[2]
        assert distance(home,extensions[direction][0])<2
    choices=[
      ('orchard-loop','Orchard & Prairie Path loop',sources['Orchard west loop'],'south','Loop · finish just before home',
       'Kenmore → Hill → Orchard → Kenilworth → Prairie Path west → Spring / Hagans → Church → Kenilworth → Adelia → Kenmore.',
       'Passes South Hill / Orchard, then makes a full western loop. No turnaround; finishes just short of home.',
       'Crosses St. Charles at Hill and Spring, York at the trail and Church, and Spring at the trail. Includes about 65 m beside St. Charles between Kenmore and Hill.'),
      ('prairie-west','Prairie Path west loop',sources['West separate crossings'],'south','Loop · finish just before home',
       'Kenmore → Marion → Kenilworth → Church → Hagans / Spring → Prairie Path east → Kenilworth → Adelia → Kenmore.',
       'A trail loop with York and St. Charles handled at separate crossings, away from their main junction.',
       'Crosses St. Charles at Spring and Kenilworth, and York at Church and the Prairie Path. Single-road crossings can still require a wait.'),
      ('prairie-east','Prairie Path east out & back',sources['Prairie east outbound'],None,'Out & back · home finish',
       'Adelia → Kenilworth → South Street connector → Prairie Path east → marked 2.50 km turnaround → same way home.',
       'Avoids York entirely. Crosses St. Charles at Kenilworth on the way out and back.',
       'Kenilworth / St. Charles still needs a crossing check. The turnaround is on the trail; mark it before the run.'),
      ('green','Glos, Wilder & quad',current,'north','Park circuit + short finish extension',
       'Glos → Wilder → university quad → Wilder garden path → York → Adelia → Kenmore.',
       'Closest to the existing event course; more park and campus paths.',
       'No St. Charles crossing. Contains the existing short backtracks around park/campus features, plus the finish extension.'),
      ('campus','Wilder & campus perimeter',sources['Wilder and campus'],'south','Park and campus circuit',
       'Kenmore / Arlington → Park → Wilder → Church → Hagans / Fairfield → Alexander → Prospect → Church → Kenmore.',
       'A larger campus circuit with fewer tiny garden turns.',
       'No St. Charles crossing. Some shared park/approach segments; verify campus access.'),
      ('prairie-return','Prairie Path west out & back',sources['Prairie west outbound'],None,'Out & back · home finish',
       'Adelia → Kenilworth → South Street connector → Prairie Path west → marked 2.50 km turnaround → same way home.',
       'Returns home exactly, crossing St. Charles at Kenilworth and York separately at the Prairie Path.',
       'Also crosses Spring on the trail. Each road crossing is repeated on the return and can still require a wait.'),
      ('west-return','West-side out & back',sources['Creek outbound'],None,'Out & back · home finish',
       'Church → Hagans / Elm Park → West Avenue → marked 2.50 km turnaround → same way home.',
       'A comparison option toward the western parks with an exact home finish.',
       'Stays north of St. Charles. Crosses York at Church twice; the western residential approach also crosses Prospect and West Avenue.'),
    ]
    routes=[]
    for key,name,source,direction,kind,description,benefit,caution in choices:
        shape=source['shape']
        if direction:
            if length(shape)<5000:
                assert distance(shape[-1],extensions[direction][0])<2
                shape=shape+extensions[direction][1:]
            shape=trim(shape,5000)
        else:
            outward=trim(shape,2500)
            shape=outward+list(reversed(outward[:-1]))
        assert min(segment_distance(YORK_ST_CHARLES,a,b) for a,b in zip(shape,shape[1:])) > 100
        assert abs(length(shape)-5000)<.01
        assert distance(shape[0],home)<.01
        offset=distance(shape[-1],home)
        assert offset<260
        routes.append(dict(id=key,name=name,km=5,meters=length(shape),shape=shape,start=shape[0],finish=shape[-1],
            finish_offset_m=round(offset),finish_direction=direction,kind=kind,description=description,
            benefit=benefit,caution=caution,backtrack_m=round(reverse_length(shape)),
            turnaround=shape[(len(shape)-1)//2] if not direction else None,
            crossings=CROSSINGS[key],
            landmarks=[{'name':'South Hill / Orchard','point':[41.887966,-87.934592]}] if key=='orchard-loop' else [],
            markers=[{'km':k,'point':trim(shape,k*1000)[-1]} for k in range(1,5)]))
        print(f'{name}: {length(shape):.2f} m; finish {offset:.0f} m from start; reversed edges {reverse_length(shape):.0f} m')
    output={'date':'2026-09-23','distance_method':'5,000 m cumulative haversine distance on routed geometry; not a certified course.',
            'start_description':'Street start by the house on Kenmore; all seven use the same point.',
            'home':home,'avoided_junction':YORK_ST_CHARLES,'routes':routes}
    (ROOT/'data/course-workshop.json').write_text(json.dumps(output,separators=(',',':'))+'\n')


if __name__=='__main__':build()
