import json,math
def spurs(shape,thresh=150):
    out=[]
    for i in range(1,len(shape)-1):
        a,b,c=shape[i-1],shape[i],shape[i+1]
        v1=(b[0]-a[0],(b[1]-a[1])*0.745); v2=(c[0]-b[0],(c[1]-b[1])*0.745)
        n1=math.hypot(*v1); n2=math.hypot(*v2)
        if n1<1e-9 or n2<1e-9: continue
        ang=math.degrees(math.acos(max(-1,min(1,(v1[0]*v2[0]+v1[1]*v2[1])/(n1*n2)))))
        if ang>thresh: out.append((i,round(b[0],5),round(b[1],5),round(ang)))
    return out
if __name__=='__main__':
    c=json.load(open('../data/course.json')); print(spurs(c['shape']))
