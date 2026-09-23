#!/usr/bin/env python3
"""Build six draft 5,000 m courses from routed source geometry.

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
      ('prairie-west','Prairie Path west loop',west,'north','Loop + short finish extension',
       'Church → Hagans / Spring → Prairie Path east → York → Adelia → Kenmore.',
       'The strongest continuous trail corridor in the heatmap; approximately 920 m on the Prairie Path.',
       'Crosses St. Charles twice. The finish extension retraces the opening stretch of Kenmore.'),
      ('prairie-east','Prairie Path east loop',sources['Prairie east via Church'],'north','Loop + short finish extension',
       'Church → York → Prairie Path east → Fair → St. Charles → Kenmore.',
       'An east-side alternative with a longer eastward trail section.',
       'Crosses St. Charles twice and uses a stretch beside it. Check the small routed jog near Fair / May.'),
      ('green','Glos, Wilder & quad',current,'north','Park circuit + short finish extension',
       'Glos → Wilder → university quad → Wilder garden path → York → Adelia → Kenmore.',
       'Closest to the existing event course; more park and campus paths.',
       'No St. Charles crossing. Contains the existing short backtracks around park/campus features, plus the finish extension.'),
      ('campus','Wilder & campus perimeter',sources['Wilder and campus'],'south','Park and campus circuit',
       'Kenmore / Arlington → Park → Wilder → Church → Hagans / Fairfield → Alexander → Prospect → Church → Kenmore.',
       'A larger campus circuit with fewer tiny garden turns.',
       'No St. Charles crossing. Some shared park/approach segments; verify campus access.'),
      ('prairie-return','Prairie Path out & back',sources['Prairie outbound'],None,'Out & back · home finish',
       'Adelia → York → Prairie Path west → marked 2.50 km turnaround → same way home.',
       'Exact same mapped start and finish. More time on the strong Prairie Path corridor.',
       'Crosses St. Charles twice. Full route is shared in both directions; the turnaround needs marking.'),
      ('west-return','West-side out & back',sources['Creek outbound'],None,'Out & back · home finish',
       'Church → Hagans / Elm Park → West Avenue → marked 2.50 km turnaround → same way home.',
       'A comparison option toward the western parks with an exact home finish.',
       'The 2.50 km turnaround is near the St. Charles corridor, before a substantial woodland section. Inspect that roadside approach.'),
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
        assert abs(length(shape)-5000)<.01
        assert distance(shape[0],home)<.01
        offset=distance(shape[-1],home)
        assert offset<260
        routes.append(dict(id=key,name=name,km=5,meters=length(shape),shape=shape,start=shape[0],finish=shape[-1],
            finish_offset_m=round(offset),finish_direction=direction,kind=kind,description=description,
            benefit=benefit,caution=caution,backtrack_m=round(reverse_length(shape)),
            turnaround=shape[(len(shape)-1)//2] if not direction else None,
            markers=[{'km':k,'point':trim(shape,k*1000)[-1]} for k in range(1,5)]))
        print(f'{name}: {length(shape):.2f} m; finish {offset:.0f} m from start; reversed edges {reverse_length(shape):.0f} m')
    output={'date':'2026-09-23','distance_method':'5,000 m cumulative haversine distance on routed geometry; not a certified course.',
            'start_description':'Street start by the house on Kenmore; all six use the same point.',
            'home':home,'routes':routes}
    (ROOT/'data/course-workshop.json').write_text(json.dumps(output,separators=(',',':'))+'\n')


if __name__=='__main__':build()
