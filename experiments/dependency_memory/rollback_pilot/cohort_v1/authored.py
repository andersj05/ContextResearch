"""Twelve original stdin/stdout tasks with independent finite test oracles.

Strata describe authored algorithmic structure; they are not benchmark ratings.
Nothing here downloads, reproduces or claims to be LiveCodeBench data.
"""
from bisect import insort
from itertools import combinations, product
import random

from ..records import ActorTask, EvaluatorTask, digest, wire

SEED = 2026100803

# Reference programs use different formulations from the small-case oracles.
SPECS = [
    ("runs", "easy", "Given n integers, output the number of maximal consecutive runs of equal values. 1 <= n <= 100000; values are signed integers.",
     "n on the first line; n integers on the second line.", "One integer: the number of runs.",
     "import sys\na=list(map(int,sys.stdin.buffer.read().split()))[1:]\nprint(1+sum(x!=y for x,y in zip(a,a[1:])))\n"),
    ("ring", "easy", "A ring has integer circumference m. Given n pairs of positions in [0,m), output the shorter distance along the ring for each pair. 2 <= m <= 1000000000; 1 <= n <= 100000.",
     "m n on the first line; n lines each contain a b.", "n lines, one shortest distance per pair.",
     "import sys\nit=iter(map(int,sys.stdin.buffer.read().split()));m=next(it);n=next(it)\nfor _ in range(n):\n a=next(it);b=next(it);d=abs(a-b);print(min(d,m-d))\n"),
    ("balance", "easy", "Start with integer balance b >= 0 and apply n signed integer changes in order. Output the one-based index of the first change making the balance negative, or 0 if it never becomes negative. Continue interpreting all input even if a failure is found. 1 <= n <= 100000.",
     "n b on the first line; n signed changes on the second line.", "One integer index, or 0.",
     "import sys\na=list(map(int,sys.stdin.buffer.read().split()));n,b=a[:2];ans=0\nfor i,x in enumerate(a[2:],1):\n b+=x\n if b<0 and ans==0: ans=i\nprint(ans)\n"),
    ("prefix", "easy", "Given n signed integers and q inclusive one-based index ranges, output each range sum. 1 <= n,q <= 100000.",
     "n q; a line of n integers; q lines l r with 1 <= l <= r <= n.", "q lines containing the requested sums.",
     "import sys\nit=iter(map(int,sys.stdin.buffer.read().split()));n=next(it);q=next(it);p=[0]\nfor _ in range(n): p.append(p[-1]+next(it))\nfor _ in range(q):\n l=next(it);r=next(it);print(p[r]-p[l-1])\n"),
    ("interval", "medium", "Choose a subset of weighted half-open intervals [s,e) with no overlap and maximum total weight. Intervals touching at an endpoint are compatible. Empty selection is allowed. 1 <= n <= 100000; 0 <= s < e <= 1000000000; weights are signed integers.",
     "n; then n lines s e weight.", "One integer: maximum total weight.",
     "import sys,bisect\nit=iter(map(int,sys.stdin.buffer.read().split()));n=next(it);a=sorted((next(it),next(it),next(it)) for _ in range(n));a.sort(key=lambda x:x[1]);ends=[x[1] for x in a];dp=[0]\nfor i,(s,e,w) in enumerate(a): dp.append(max(dp[-1],dp[bisect.bisect_right(ends,s,0,i)]+w))\nprint(dp[-1])\n"),
    ("bottleneck", "medium", "For an undirected weighted graph, find a path from vertex 1 to vertex n minimizing the largest edge weight on the path. Output -1 when unreachable; for n=1 output 0. Parallel edges are allowed. 1 <= n <= 100000, 0 <= m <= 200000, nonnegative weights <= 1000000000.",
     "n m; then m lines u v weight, with vertices numbered 1..n.", "One integer: minimum bottleneck or -1.",
     "import sys,heapq\nit=iter(map(int,sys.stdin.buffer.read().split()));n=next(it);m=next(it);g=[[] for _ in range(n)]\nfor _ in range(m):\n u=next(it)-1;v=next(it)-1;w=next(it);g[u].append((v,w));g[v].append((u,w))\nd=[10**30]*n;d[0]=0;h=[(0,0)]\nwhile h:\n x,u=heapq.heappop(h)\n if x!=d[u]: continue\n for v,w in g[u]:\n  y=max(x,w)\n  if y<d[v]: d[v]=y;heapq.heappush(h,(y,v))\nprint(-1 if d[-1]==10**30 else d[-1])\n"),
    ("modrange", "medium", "Count the nonempty contiguous subarrays whose sum is divisible by k. Integers may be negative. 1 <= n <= 200000; 1 <= k <= 1000000000.",
     "n k; then n signed integers.", "One integer count.",
     "import sys\nit=iter(map(int,sys.stdin.buffer.read().split()));n=next(it);k=next(it);seen={0:1};s=ans=0\nfor x in it:\n s=(s+x)%k;ans+=seen.get(s,0);seen[s]=seen.get(s,0)+1\nprint(ans)\n"),
    ("anagram", "medium", "Count the contiguous windows of text with length equal to the pattern that can be rearranged into the pattern. A '?' in the pattern matches any single lowercase letter; text contains only lowercase letters. If the pattern is longer than the text, output 0. Both lengths are between 1 and 200000.",
     "Text on the first line; pattern on the second line.", "One integer count.",
     "import sys\nfrom collections import Counter\ns,p=sys.stdin.read().split();m=len(p);need=Counter(p.replace('?',''));have=Counter();ans=0\nfor i,c in enumerate(s):\n have[c]+=1\n if i>=m: have[s[i-m]]-=1\n if i>=m-1 and all(have[c]>=n for c,n in need.items()): ans+=1\nprint(ans)\n"),
    ("treecover", "hard", "Find the minimum total cost of a vertex cover of a tree: every edge must have at least one endpoint selected. Costs are nonnegative. For a one-vertex tree the empty set is valid. 1 <= n <= 200000; costs <= 1000000000.",
     "n; n costs; then n-1 undirected edges u v, vertices 1..n.", "One integer minimum cost.",
     "import sys\nit=iter(map(int,sys.stdin.buffer.read().split()));n=next(it);cost=[next(it) for _ in range(n)];g=[[] for _ in range(n)]\nfor _ in range(n-1):\n u=next(it)-1;v=next(it)-1;g[u].append(v);g[v].append(u)\npar=[-1]*n;order=[0]\nfor u in order:\n for v in g[u]:\n  if v!=par[u]: par[v]=u;order.append(v)\noff=[0]*n;on=cost[:]\nfor u in reversed(order):\n for v in g[u]:\n  if par[v]==u: off[u]+=on[v];on[u]+=min(off[v],on[v])\nprint(min(off[0],on[0]))\n"),
    ("orderstat", "hard", "Process q operations on an initially empty multiset of signed integers. '+ x' inserts one x. '- x' deletes one x if present, otherwise does nothing. '? k' asks for the kth smallest element with one-based k, outputting NONE if k<1 or k exceeds the size. Duplicates count separately. 1 <= q <= 200000; |x| <= 1000000000.",
     "q; then q lines '+ x', '- x' or '? k'.", "One line per query: an integer or NONE.",
     "import sys,bisect\na=[x.split() for x in sys.stdin.read().splitlines()[1:]];xs=sorted({int(v) for op,v in a if op!='?'});bit=[0]*(len(xs)+1);cnt=[0]*len(xs);total=0\ndef add(i,d):\n i+=1\n while i<len(bit): bit[i]+=d;i+=i&-i\nfor op,val in a:\n x=int(val)\n if op=='?':\n  if x<1 or x>total: print('NONE');continue\n  pos=0;step=1<<len(xs).bit_length()\n  while step:\n   nxt=pos+step\n   if nxt<len(bit) and bit[nxt]<x: x-=bit[nxt];pos=nxt\n   step//=2\n  print(xs[pos])\n else:\n  i=bisect.bisect_left(xs,x)\n  if op=='+': cnt[i]+=1;total+=1;add(i,1)\n  elif cnt[i]>0: cnt[i]-=1;total-=1;add(i,-1)\n"),
    ("brackets", "hard", "Replace every '?' in a parentheses string by '(' or ')' so that every prefix has at least as many opens as closes and the total counts match. Each '?' has a given cost for '(' and another cost for ')'. Fixed parentheses have zero cost. Output the minimum cost, or -1 if impossible. 1 <= length <= 200000; each cost is an integer in [0,1000000000].",
     "The string; then one line open_cost close_cost for each '?' in left-to-right order.", "One integer: minimum cost or -1.",
     "import sys,heapq\nit=iter(sys.stdin.read().split());s=next(it);balance=cost=0;h=[];bad=False\nfor c in s:\n if c=='(': balance+=1\n else:\n  balance-=1\n  if c=='?':\n   a=int(next(it));b=int(next(it));cost+=b;heapq.heappush(h,a-b)\n  if balance<0:\n   if not h: bad=True;break\n   cost+=heapq.heappop(h);balance+=2\nprint(-1 if bad or balance else cost)\n"),
    ("segmentation", "hard", "Cover a lowercase string by concatenating dictionary words, minimizing the total word cost. A word can be reused. Duplicate words with different costs are allowed. Output -1 if no cover exists. Text length <= 100000; at most 2000 words; each word has length 1..30 and nonnegative cost <= 1000000000.",
     "The text; number d; then d lines word cost.", "One integer: minimum cost or -1.",
     "import sys\na=sys.stdin.read().split();s=a[0];d=int(a[1]);words={}\nfor i in range(d):\n w=a[2+2*i];c=int(a[3+2*i]);words[w]=min(words.get(w,10**30),c)\nlengths=sorted({len(w) for w in words});dp=[10**30]*(len(s)+1);dp[0]=0\nfor i in range(1,len(s)+1):\n for n in lengths:\n  if n>i: break\n  w=s[i-n:i]\n  if w in words: dp[i]=min(dp[i],dp[i-n]+words[w])\nprint(-1 if dp[-1]==10**30 else dp[-1])\n"),
]


def case(name, seed, size=8):
    rng = random.Random(seed)
    if name == "runs":
        a = [rng.randrange(-2, 3) for _ in range(size)]
        groups, start = 0, 0
        while start < len(a):
            end = start + 1
            while end < len(a) and a[end] == a[start]:
                end += 1
            groups += 1
            start = end
        return f"{len(a)}\n" + " ".join(map(str, a)) + "\n", f"{groups}\n"
    if name == "ring":
        m = rng.randint(2, 50)
        pairs = [(rng.randrange(m), rng.randrange(m)) for _ in range(size)]
        expected = [min((a-b) % m, (b-a) % m) for a,b in pairs]
        return f"{m} {size}\n" + "".join(f"{a} {b}\n" for a,b in pairs), "".join(f"{x}\n" for x in expected)
    if name == "balance":
        b = rng.randrange(12)
        a = [rng.randint(-5, 5) for _ in range(size)]
        bad = [i for i in range(1, size+1) if b+sum(a[:i]) < 0]
        return f"{size} {b}\n" + " ".join(map(str, a)) + "\n", f"{min(bad) if bad else 0}\n"
    if name == "prefix":
        a = [rng.randint(-20, 20) for _ in range(size)]
        ranges = [sorted((rng.randint(1, size), rng.randint(1, size))) for _ in range(size)]
        return f"{size} {size}\n" + " ".join(map(str, a)) + "\n" + "".join(f"{l} {r}\n" for l,r in ranges), "".join(f"{sum(a[l-1:r])}\n" for l,r in ranges)
    if name == "interval":
        a = [(s := rng.randrange(15), s+rng.randrange(1, 7), rng.randint(-10, 20)) for _ in range(min(size, 12))]
        best = 0
        for mask in range(1 << len(a)):
            chosen = sorted(a[i] for i in range(len(a)) if mask >> i & 1)
            if all(x[1] <= y[0] for x,y in zip(chosen, chosen[1:])):
                best = max(best, sum(x[2] for x in chosen))
        return f"{len(a)}\n" + "".join(f"{s} {e} {w}\n" for s,e,w in a), f"{best}\n"
    if name == "bottleneck":
        n = min(size, 10)
        edges = [(u,v,rng.randint(0,20)) for u,v in combinations(range(n),2) if rng.random()<.25]
        inf = 10**20
        distances = [[0 if u==v else inf for v in range(n)] for u in range(n)]
        for u,v,w in edges:
            distances[u][v] = distances[v][u] = min(distances[u][v], w)
        for k in range(n):
            for i in range(n):
                for j in range(n):
                    distances[i][j] = min(distances[i][j], max(distances[i][k], distances[k][j]))
        ans = distances[0][-1]
        return f"{n} {len(edges)}\n" + "".join(f"{u+1} {v+1} {w}\n" for u,v,w in edges), f"{-1 if ans==inf else ans}\n"
    if name == "modrange":
        k = rng.randint(1, 9)
        a = [rng.randint(-7,7) for _ in range(size)]
        expected = sum(sum(a[i:j]) % k == 0 for i in range(size) for j in range(i+1,size+1))
        return f"{size} {k}\n" + " ".join(map(str,a)) + "\n", f"{expected}\n"
    if name == "anagram":
        text = "".join(rng.choice("abc") for _ in range(size))
        pattern = "".join(rng.choice("abc?") for _ in range(rng.randint(1,size+2)))
        needed = [c for c in pattern if c!='?']
        ans = 0
        for i in range(len(text)-len(pattern)+1):
            remaining = list(text[i:i+len(pattern)])
            for c in needed:
                if c not in remaining:
                    break
                remaining.remove(c)
            else:
                ans += 1
        return f"{text}\n{pattern}\n", f"{ans}\n"
    if name == "treecover":
        n = min(size, 14)
        cost = [rng.randrange(15) for _ in range(n)]
        edges = [(rng.randrange(i), i) for i in range(1,n)]
        ans = min(sum(cost[i] for i in range(n) if mask>>i&1) for mask in range(1<<n)
                  if all(mask>>u&1 or mask>>v&1 for u,v in edges))
        return f"{n}\n" + " ".join(map(str,cost)) + "\n" + "".join(f"{u+1} {v+1}\n" for u,v in edges), f"{ans}\n"
    if name == "orderstat":
        operations, state, output = [], [], []
        for _ in range(size):
            op = rng.choice("++--??")
            x = rng.randint(-3,12) if op=='?' else rng.randint(-5,5)
            operations.append(f"{op} {x}\n")
            if op=='+':
                insort(state,x)
            elif op=='-':
                if x in state:
                    state.remove(x)
            else:
                output.append(str(state[x-1]) if 1<=x<=len(state) else "NONE")
        if not output:
            operations.append("? 1\n")
            output.append(str(state[0]) if state else "NONE")
        return f"{len(operations)}\n" + "".join(operations), "\n".join(output)+"\n"
    if name == "brackets":
        text = "".join(rng.choice("()?" ) for _ in range(min(size,14)))
        costs = [(rng.randrange(12),rng.randrange(12)) for c in text if c=='?']
        best = None
        for assignment in product("()", repeat=len(costs)):
            cursor = balance = cost = 0
            valid = True
            for c in text:
                if c=='?':
                    c=assignment[cursor];cost+=costs[cursor][c==')'];cursor+=1
                balance += 1 if c=='(' else -1
                if balance<0:
                    valid=False
                    break
            if valid and balance==0:
                best = cost if best is None else min(best,cost)
        return text+"\n"+"".join(f"{a} {b}\n" for a,b in costs), f"{-1 if best is None else best}\n"
    if name == "segmentation":
        text = "".join(rng.choice("ab") for _ in range(min(size,12)))
        words = [("".join(rng.choice("ab") for _ in range(rng.randint(1,4))),rng.randrange(12)) for _ in range(9)]
        best = [None]
        def enumerate_covers(pos,total):
            if pos==len(text):
                best[0]=total if best[0] is None else min(best[0],total)
                return
            for word,cost in words:
                if text.startswith(word,pos):
                    enumerate_covers(pos+len(word),total+cost)
        enumerate_covers(0,0)
        return text+f"\n{len(words)}\n"+"".join(f"{w} {c}\n" for w,c in words), f"{-1 if best[0] is None else best[0]}\n"
    raise ValueError("unknown authored task")


def stress(name):
    n = 5000
    if name == "runs": return f"{n}\n"+"7 "*n+"\n", "1\n"
    if name == "ring": return f"1000000000 {n}\n"+"0 999999999\n"*n, "1\n"*n
    if name == "balance": return f"{n} 0\n"+"0 "*(n-1)+"-1\n", f"{n}\n"
    if name == "prefix": return f"{n} 2\n"+"1 "*n+f"\n1 {n}\n{n} {n}\n", f"{n}\n1\n"
    if name == "interval": return f"{n}\n"+"".join(f"{i} {i+1} 1\n" for i in range(n)), f"{n}\n"
    if name == "bottleneck": return f"{n} {n-1}\n"+"".join(f"{i} {i+1} {i}\n" for i in range(1,n)), f"{n-1}\n"
    if name == "modrange": return f"{n} 1\n"+"0 "*n+"\n", f"{n*(n+1)//2}\n"
    if name == "anagram": return "a"*n+"\n???\n", f"{n-2}\n"
    if name == "treecover": return f"{n}\n"+"1 "*n+"\n"+"".join(f"1 {i}\n" for i in range(2,n+1)), "1\n"
    if name == "orderstat": return f"{n+3}\n"+"+ -7\n"*n+f"? {n}\n- -7\n? {n}\n", "-7\nNONE\n"
    if name == "brackets": return "?"*n+"\n"+"1 2\n"*n, f"{3*n//2}\n"
    if name == "segmentation": return "a"*n+"\n3\na 3\naa 4\naaa 5\n", f"{5*(n//3)+4}\n"
    raise ValueError("unknown stress task")


def generate():
    cohort = []
    for index,(name,stratum,statement,input_format,output_format,reference) in enumerate(SPECS):
        tests=[]
        for slot in range(12):
            size = (1, 6, 2, 3, 7, 8, 9, 10, 12, 14, 11, 5)[slot]
            stdin,stdout = case(name, SEED+100*index+slot, size)
            tests.append({"id": ("public" if slot<2 else "reserved")+str(slot+1), "input": stdin, "output": stdout})
        stdin,stdout=stress(name)
        tests.append({"id":"reserved-stress", "input":stdin, "output":stdout})
        task=ActorTask.from_dict("authored-code-"+name,stratum,{"domain":"coding","statement":statement,
            "input_format":input_format,"output_format":output_format,"public_examples":tests[:2]})
        evaluator=EvaluatorTask.bind(task,{"private_tests":tests[2:],"reference_code":reference,
            "reference_provenance":"Original repository-authored program; independent finite oracle and closed-form stress output in cohort_v1/authored.py",
            "reference_sha256":digest(reference),"private_tests_sha256":digest(wire(tests[2:])),
            "origin":{"source":"repository-authored coding cohort v1","seed":SEED+100*index,"family":name,
                      "stratum_scope":"authored structural complexity; not a benchmark difficulty rating"},
            "license_review":{"permitted":True,"source":"original repository-authored statement, tests and reference", "reviewer":"implementation author"},
            "retained_tests_complete":True,"benchmark_claim":"Not LiveCodeBench; source/distribution amendment"})
        cohort.append((task,evaluator))
    return cohort
