from fractions import Fraction
from time import perf_counter
import json
from pathlib import Path

WORDS=tuple(range(16))
LOSS=tuple(tuple(3*x.bit_count()+3*a.bit_count()-2*x.bit_count()*a.bit_count()+2*(x&a).bit_count() for a in WORDS) for x in range(16))

def layers(g):
    rows={0:(1,)}
    for length in range(1,g+1):
        size=16**(length-1)
        following={}
        for prefix,old in rows.items():
            for i,a in enumerate(WORDS):
                histogram=[0]*(12*length+1)
                for x in range(16):
                    cost=LOSS[x][i]
                    shift=x*size
                    for previous,mask in enumerate(old):
                        if mask:
                            histogram[previous+cost] |= mask << shift
                following[prefix | (a << (4*(length-1)))]=tuple(histogram)
        rows=following
    return rows

def run(g):
    started=perf_counter()
    data=layers(g)
    covers={w:0 for w in data}
    population=(1 << (16**g))-1
    result=[]
    for threshold in range(12*g+1):
        for w,row in data.items():
            covers[w] |= row[threshold]
        remaining=population ^ covers[0]
        book=[0]
        gains=[]
        for _ in range(4**g-1):
            chosen=max(covers,key=lambda w:((covers[w]&remaining).bit_count(),-w))
            gain=(covers[chosen]&remaining).bit_count()
            if not gain:
                break
            book.append(chosen)
            gains.append(gain)
            remaining &= ~covers[chosen]
        ungraded=population
        errors=0
        for level in range(12*g+1):
            mask=0
            for w in book:
                mask |= data[w][level]
            newly=mask&ungraded
            errors += level*newly.bit_count()
            ungraded &= ~newly
        assert not ungraded
        result.append({"threshold":threshold,"book":book,"gains":gains,
                       "uncovered":remaining.bit_count(),"errors":errors,
                       "error":str(Fraction(errors,12*g*16**g))})
    best=min(result,key=lambda r:(r["errors"],r["threshold"]))
    print(g,best["threshold"],best["error"],float(Fraction(best["error"])),len(best["book"]),perf_counter()-started,flush=True)
    return {"group":g,"rows":result,"best":best}

out=[run(g) for g in (1,2,3)]
Path("build/greedy-cover/probe.json").write_text(json.dumps(out,indent=2)+"\n")
