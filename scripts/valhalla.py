import json,subprocess
def _call(pts):
    body={"locations":[{"lat":a,"lon":b,"type":"through"} for a,b in pts],"costing":"pedestrian","directions_options":{"units":"kilometers"}}
    body["locations"][0]["type"]="break"; body["locations"][-1]["type"]="break"
    out=subprocess.run(['curl','-s','-m','60','-X','POST','https://valhalla1.openstreetmap.de/route','-H','Content-Type: application/json','-H','User-Agent: fc5k/1.0','-d',json.dumps(body)],capture_output=True,text=True).stdout
    j=json.loads(out)
    if 'trip' not in j: raise Exception(j)
    return j['trip']
def decode(s):
    # polyline6
    idx=0;lat=0;lon=0;out=[]
    while idx<len(s):
        for which in (0,1):
            res=0;shift=0
            while True:
                b=ord(s[idx])-63; idx+=1; res|=(b&0x1f)<<shift; shift+=5
                if b<0x20: break
            d=~(res>>1) if res&1 else res>>1
            if which==0: lat+=d
            else: lon+=d
        out.append((lat/1e6,lon/1e6))
    return out
def route(pts):
    # chunk into <=10 locations, overlapping
    L=0; names=[]; shape=[]
    i=0
    while i<len(pts)-1:
        chunk=pts[i:i+10]; t=_call(chunk); L+=t['summary']['length']
        for leg in t['legs']:
            names+=[m['street_names'][0] for m in leg['maneuvers'] if m.get('street_names')]
            pl=decode(leg['shape']); shape+=pl[1:] if shape else pl
        i+=9
    d=[]; [d.append(n) for n in names if not d or d[-1]!=n]
    return L,d,shape
