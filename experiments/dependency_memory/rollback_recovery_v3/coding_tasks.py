"""Eight coupled algorithmic tasks, four seeded instances each; original sources."""
from collections import Counter
from itertools import combinations, product
import random
from textwrap import dedent

from ..rollback_pilot.records import ActorTask, EvaluatorTask, digest, wire

SEED=2026100829

SPECS={
"interval_k":("Choose exactly k mutually nonoverlapping weighted half-open intervals [s,e), maximizing total weight. Endpoint-touching intervals are compatible, weights may be negative, and k=0 has value 0. Output IMPOSSIBLE if no such subset exists. 1<=n<=5000, 0<=k<=min(n,30), 0<=s<e<=10^9, |weight|<=10^9.","n k; then n lines s e weight.","One integer maximum weight, or IMPOSSIBLE.",r'''
import sys,bisect
it=iter(map(int,sys.stdin.buffer.read().split()));n=next(it);k=next(it)
a=[(next(it),next(it),next(it)) for _ in range(n)];a.sort(key=lambda x:x[1]);ends=[x[1] for x in a]
previous=[bisect.bisect_right(ends,s,0,i) for i,(s,e,w) in enumerate(a)]
old=[0]*(n+1)
for used in range(1,k+1):
 new=[None]*(n+1)
 for i,(s,e,w) in enumerate(a,1):
  value=old[previous[i-1]]
  take=None if value is None else value+w
  skip=new[i-1]
  new[i]=take if skip is None else skip if take is None else max(skip,take)
 old=new
print('IMPOSSIBLE' if old[n] is None else old[n])
'''),
"xor_cost":("Assign a bit x[v] to every vertex of an undirected constraint graph. Each edge (u,v,p) requires x[u] XOR x[v]=p. Selecting x[v]=1 costs c[v]>=0; selecting 0 costs zero. Minimize total cost, or output IMPOSSIBLE for inconsistent constraints. Duplicate edges and self-loops are allowed. 1<=n<=100000, 0<=m<=200000, costs<=10^9, p is 0 or 1.","n m; n costs; then m lines u v p with vertices 1..n.","One integer minimum cost, or IMPOSSIBLE.",r'''
import sys
it=iter(map(int,sys.stdin.buffer.read().split()));n=next(it);m=next(it);cost=[next(it) for _ in range(n)];g=[[] for _ in range(n)]
for _ in range(m):
 u=next(it)-1;v=next(it)-1;p=next(it);g[u].append((v,p));g[v].append((u,p))
color=[-1]*n;ans=0;bad=False
for root in range(n):
 if color[root]!=-1:continue
 color[root]=0;order=[root];tot=ones=0
 for u in order:
  tot+=cost[u];ones+=cost[u]*color[u]
  for v,p in g[u]:
   want=color[u]^p
   if color[v]==-1:color[v]=want;order.append(v)
   elif color[v]!=want:bad=True
 ans+=min(ones,tot-ones)
print('IMPOSSIBLE' if bad else ans)
'''),
"tree_k":("Choose exactly k vertices forming a vertex cover of a tree: every edge must have a selected endpoint. Minimize total nonnegative vertex cost. For a one-vertex tree k=0 is valid. Output IMPOSSIBLE when no exact-size cover exists. 1<=n<=200, 0<=k<=min(n,30), costs<=10^9.","n k; n costs; then n-1 lines u v (vertices 1..n).","One integer minimum cost, or IMPOSSIBLE.",r'''
import sys
it=iter(map(int,sys.stdin.buffer.read().split()));n=next(it);k=next(it);cost=[next(it) for _ in range(n)];g=[[] for _ in range(n)]
for _ in range(n-1):
 u=next(it)-1;v=next(it)-1;g[u].append(v);g[v].append(u)
parent=[-1]*n;order=[0]
for u in order:
 for v in g[u]:
  if v!=parent[u]:parent[v]=u;order.append(v)
inf=10**30;off=[None]*n;on=[None]*n
def merge(a,b):
 z=[inf]*min(k+1,len(a)+len(b)-1)
 for i,x in enumerate(a):
  for j,y in enumerate(b):
   if i+j<len(z):z[i+j]=min(z[i+j],x+y)
 return z
for u in reversed(order):
 a=[0,inf][:k+1];b=[inf,cost[u]][:k+1]
 for v in g[u]:
  if parent[v]==u:
   a=merge(a,on[v]);best=[min(x,y) for x,y in zip(off[v],on[v])];b=merge(b,best)
 off[u],on[u]=a,b
answer=min(off[0][k] if k<len(off[0]) else inf,on[0][k] if k<len(on[0]) else inf)
print('IMPOSSIBLE' if answer>=inf else answer)
'''),
"digit_range":("Count integers x in inclusive [L,R] whose ordinary decimal representation has no identical adjacent digits and whose digit sum is congruent to r modulo k. Leading zeroes are not part of the representation. The integer 0 has representation '0' and digit sum 0. 0<=L<=R<=10^18, 1<=k<=20, 0<=r<k.","L R k r.","One integer count.",r'''
import sys
from functools import lru_cache
lo,hi,k,target=map(int,sys.stdin.read().split())
def count(bound):
 if bound<0:return 0
 digits=tuple(map(int,str(bound)))
 @lru_cache(None)
 def visit(i,tight,last,total):
  if i==len(digits):return int(total==target)
  ans=0;maximum=digits[i] if tight else 9
  for d in range(maximum+1):
   nt=tight and d==maximum
   if last==10 and d==0:ans+=visit(i+1,nt,10,total)
   elif d!=last:ans+=visit(i+1,nt,d,(total+d)%k)
  return ans
 return visit(0,True,10,0)
print(count(hi)-count(lo-1))
'''),
"dynamic_connectivity":("Process operations on a graph initially without edges. '+ u v' adds one copy of an undirected edge; '- u v' removes one copy if any exist and otherwise does nothing; '? u' asks for the number of vertices connected to u, including u. Multiple copies and self-loops are allowed. An edge connects vertices while its multiplicity is positive. 1<=n<=100000, 1<=q<=100000.","n q; q operation lines, each '+ u v', '- u v' or '? u'. Vertices 1..n.","One integer component size per query.",r'''
import sys
raw=sys.stdin.read().splitlines();n,q=map(int,raw[0].split());ops=[x.split() for x in raw[1:]];active={};intervals=[]
for t,op in enumerate(ops):
 if op[0]=='?':continue
 u,v=sorted((int(op[1])-1,int(op[2])-1));edge=(u,v);count,start=active.get(edge,(0,0))
 if op[0]=='+':
  if count==0:start=t
  active[edge]=(count+1,start)
 elif count:
  if count==1:intervals.append((start,t,edge))
  active[edge]=(count-1,start)
for edge,(count,start) in active.items():
 if count:intervals.append((start,q,edge))
tree=[[] for _ in range(4*q)]
def insert(node,lo,hi,a,b,edge):
 if a>=hi or b<=lo:return
 if a<=lo and hi<=b:tree[node].append(edge);return
 mid=(lo+hi)//2;insert(node*2,lo,mid,a,b,edge);insert(node*2+1,mid,hi,a,b,edge)
for a,b,e in intervals:
 if a<b:insert(1,0,q,a,b,e)
parent=list(range(n));size=[1]*n;changes=[];out=[]
def find(u):
 while parent[u]!=u:u=parent[u]
 return u
def visit(node,lo,hi):
 checkpoint=len(changes)
 for u,v in tree[node]:
  u=find(u);v=find(v)
  if u==v:continue
  if size[u]<size[v]:u,v=v,u
  changes.append((v,u,size[u]));parent[v]=u;size[u]+=size[v]
 if hi-lo==1:
  if ops[lo][0]=='?':out.append(str(size[find(int(ops[lo][1])-1)]))
 else:
  mid=(lo+hi)//2;visit(node*2,lo,mid);visit(node*2+1,mid,hi)
 while len(changes)>checkpoint:
  v,u,old=changes.pop();parent[v]=v;size[u]=old
visit(1,0,q);print('\n'.join(out))
'''),
"gf2_lex":("Solve m linear equations over binary variables x1..xn with XOR addition, returning the lexicographically smallest satisfying bitstring x1...xn (0 precedes 1). Each coefficient row is a length-n binary string whose leftmost bit multiplies x1. Zero rows, duplicate equations and m=0 are allowed. Output IMPOSSIBLE if inconsistent. 1<=n<=60, 0<=m<=100.","n m; m lines coefficient_bitstring rhs (rhs 0 or 1).","One n-character binary string, or IMPOSSIBLE.",r'''
import sys
it=iter(sys.stdin.read().split());n=int(next(it));m=int(next(it));rows=[(int(next(it),2),int(next(it))) for _ in range(m)]
def possible(equations):
 basis={}
 for mask,b in equations:
  while mask:
   p=mask.bit_length()-1
   if p not in basis:basis[p]=(mask,b);break
   other,rhs=basis[p];mask^=other;b^=rhs
  else:
   if b:return False
 return True
if not possible(rows):print('IMPOSSIBLE')
else:
 out=[]
 for i in range(n):
  mask=1<<(n-1-i);b=0 if possible(rows+[(mask,0)]) else 1
  rows.append((mask,b));out.append(str(b))
 print(''.join(out))
'''),
"two_machines":("Choose a subset of weighted half-open intervals [s,e) so no time belongs to more than TWO chosen intervals. Maximize total weight; negative weights may be skipped and the empty subset is allowed. Touching endpoints do not overlap. Duplicate intervals are distinct choices. 1<=n<=2000, 0<=s<e<=10^9, |weight|<=10^9.","n; n lines s e weight.","One integer maximum weight.",r'''
import sys,heapq
it=iter(map(int,sys.stdin.read().split()));n=next(it);a=[(next(it),next(it),next(it)) for _ in range(n)];times=sorted({x for s,e,w in a for x in (s,e)});index={x:i for i,x in enumerate(times)};v=len(times);g=[[] for _ in range(v)]
def edge(u,w,cap,cost):
 g[u].append([w,len(g[w]),cap,cost]);g[w].append([u,len(g[u])-1,0,-cost])
for i in range(v-1):edge(i,i+1,2,0)
for s,e,w in a:edge(index[s],index[e],1,-w)
inf=10**30;potential=[inf]*v;potential[0]=0
for u in range(v):
 for dest,rev,cap,cost in g[u]:
  if cap:potential[dest]=min(potential[dest],potential[u]+cost)
flow=cost_total=0
while flow<2:
 dist=[inf]*v;dist[0]=0;previous=[None]*v;queue=[(0,0)]
 while queue:
  distance,u=heapq.heappop(queue)
  if distance!=dist[u]:continue
  for i,(dest,rev,cap,cost) in enumerate(g[u]):
   if cap:
    new=distance+cost+potential[u]-potential[dest]
    if new<dist[dest]:dist[dest]=new;previous[dest]=(u,i);heapq.heappush(queue,(new,dest))
 for u in range(v):
  if dist[u]<inf:potential[u]+=dist[u]
 amount=2-flow;u=v-1
 while u:
  p,i=previous[u];amount=min(amount,g[p][i][2]);u=p
 u=v-1
 while u:
  p,i=previous[u];item=g[p][i];cost_total+=amount*item[3];item[2]-=amount;g[u][item[1]][2]+=amount;u=p
 flow+=amount
print(-cost_total)
'''),
"grid_turns":("Find a minimum-cost path from the top-left to bottom-right cell of a grid, moving only right or down, using exactly k direction changes. The first move is not a direction change. Blocked cells cannot be visited; start or end may be blocked. Cell costs may be negative and every visited cell, including start/end, contributes once. A one-cell path has zero changes. 1<=n,m<=30, 0<=k<=20, |cost|<=1000.","n m k; n rows of m integer costs; n strings of length m using '.' for open and '#' for blocked.","One integer minimum cost, or IMPOSSIBLE.",r'''
import sys
from functools import lru_cache
it=iter(sys.stdin.read().split());n=int(next(it));m=int(next(it));k=int(next(it));cost=[[int(next(it)) for _ in range(m)] for _ in range(n)];grid=[next(it) for _ in range(n)];inf=10**30
@lru_cache(None)
def solve(r,c,last,turns):
 if r>=n or c>=m or grid[r][c]=='#' or turns>k:return inf
 if r==n-1 and c==m-1:return cost[r][c] if turns==k else inf
 best=inf
 for direction,(dr,dc) in enumerate(((0,1),(1,0))):
  extra=int(last!=2 and last!=direction);best=min(best,solve(r+dr,c+dc,direction,turns+extra))
 return cost[r][c]+best if best<inf else inf
answer=solve(0,0,2,0);print('IMPOSSIBLE' if answer>=inf else answer)
''')}


def expected(name, payload):
    """Small-instance oracles deliberately use exhaustive alternatives to refs."""
    if name in {"interval_k","two_machines"}:
        intervals,k=payload;best=None if name=="interval_k" and k else 0
        for mask in range(1<<len(intervals)):
            if name=="interval_k" and mask.bit_count()!=k:continue
            chosen=[x for i,x in enumerate(intervals) if mask>>i&1]
            events=sorted([(s,1) for s,e,w in chosen]+[(e,-1) for s,e,w in chosen])
            active=0;valid=True
            for t,change in events:
                active+=change
                if active>(1 if name=="interval_k" else 2):valid=False;break
            if valid:
                value=sum(w for s,e,w in chosen);best=value if best is None else max(best,value)
        return 'IMPOSSIBLE' if best is None else str(best)
    if name=="xor_cost":
        costs,edges=payload;best=None
        for bits in product((0,1),repeat=len(costs)):
            if all(bits[u]^bits[v]==p for u,v,p in edges):
                value=sum(c*x for c,x in zip(costs,bits));best=value if best is None else min(best,value)
        return 'IMPOSSIBLE' if best is None else str(best)
    if name=="tree_k":
        costs,edges,k=payload;best=None
        for vertices in combinations(range(len(costs)),k):
            selected=set(vertices)
            if all(u in selected or v in selected for u,v in edges):
                value=sum(costs[u] for u in selected);best=value if best is None else min(best,value)
        return 'IMPOSSIBLE' if best is None else str(best)
    if name=="digit_range":
        lo,hi,k,r=payload
        return str(sum(all(a!=b for a,b in zip(str(x),str(x)[1:])) and sum(map(int,str(x)))%k==r for x in range(lo,hi+1)))
    if name=="dynamic_connectivity":
        n,ops=payload;edges=Counter();out=[]
        for op in ops:
            if op[0]=='?':
                reached={op[1]};pending=[op[1]]
                for u in pending:
                    for (a,b),count in edges.items():
                        if count and u in (a,b):
                            v=b if a==u else a
                            if v not in reached:reached.add(v);pending.append(v)
                out.append(str(len(reached)))
            else:
                key=tuple(sorted(op[1:]));edges[key]+=1 if op[0]=='+' else -int(edges[key]>0)
        return '\n'.join(out)
    if name=="gf2_lex":
        n,rows=payload
        for value in range(1<<n):
            if all((value&int(coeff,2)).bit_count()%2==rhs for coeff,rhs in rows):return f'{value:0{n}b}'
        return 'IMPOSSIBLE'
    if name=="grid_turns":
        costs,grid,k=payload;n=len(costs);m=len(costs[0]);length=n+m-2;best=None
        for down_positions in combinations(range(length),n-1):
            down=set(down_positions);r=c=0;value=costs[0][0];valid=grid[0][0]!='#';last=None;turns=0
            for step in range(length):
                direction=int(step in down);turns+=int(last is not None and direction!=last);last=direction
                r+=direction;c+=1-direction;value+=costs[r][c];valid &= grid[r][c]!='#'
            if valid and turns==k:best=value if best is None else min(best,value)
        return 'IMPOSSIBLE' if best is None else str(best)
    raise ValueError(name)


def serialize(name,payload):
    if name in {"interval_k","two_machines"}:
        a,k=payload
        return (f"{len(a)} {k}\n" if name=="interval_k" else f"{len(a)}\n")+''.join(f"{s} {e} {w}\n" for s,e,w in a)
    if name=="xor_cost":
        costs,edges=payload
        return f"{len(costs)} {len(edges)}\n"+' '.join(map(str,costs))+'\n'+''.join(f"{u+1} {v+1} {p}\n" for u,v,p in edges)
    if name=="tree_k":
        costs,edges,k=payload
        return f"{len(costs)} {k}\n"+' '.join(map(str,costs))+'\n'+''.join(f"{u+1} {v+1}\n" for u,v in edges)
    if name=="digit_range":return ' '.join(map(str,payload))+'\n'
    if name=="dynamic_connectivity":
        n,ops=payload
        return f"{n} {len(ops)}\n"+''.join(op[0]+' '+' '.join(str(x+1) for x in op[1:])+'\n' for op in ops)
    if name=="gf2_lex":
        n,rows=payload
        return f"{n} {len(rows)}\n"+''.join(f"{mask} {b}\n" for mask,b in rows)
    if name=="grid_turns":
        costs,grid,k=payload
        return f"{len(costs)} {len(costs[0])} {k}\n"+''.join(' '.join(map(str,row))+'\n' for row in costs)+'\n'.join(grid)+'\n'
    raise ValueError(name)


def case(name,seed,size,slot):
    rng=random.Random(seed)
    if name in {"interval_k","two_machines"}:
        a=[(s:=rng.randrange(10),s+rng.randint(1,6),rng.randint(-8,20)) for _ in range(size)]
        k=rng.randint(0,min(size,5))
        if slot==0:a=[(0,1,-4)];k=1
        if slot==1:a=[(0,2,4),(2,3,5),(0,3,20)];k=2
        payload=a,k
    elif name=="xor_cost":
        costs=[rng.randrange(20) for _ in range(size)]
        edges=[(rng.randrange(size),rng.randrange(size),rng.randrange(2)) for _ in range(size+3)]
        if slot==0:costs=[4];edges=[(0,0,0)]
        if slot==1:costs=[8,3];edges=[(0,1,1),(0,1,1)]
        payload=costs,edges
    elif name=="tree_k":
        costs=[rng.randrange(20) for _ in range(size)];edges=[(rng.randrange(v),v) for v in range(1,size)];k=rng.randint(0,size)
        if slot==0:costs=[9];edges=[];k=0
        if slot==1:costs=[20,1,1];edges=[(0,1),(0,2)];k=1
        payload=costs,edges,k
    elif name=="digit_range":
        lo=rng.randrange(300);hi=lo+rng.randrange(400);k=rng.randint(1,8);r=rng.randrange(k)
        if slot==0:lo,hi,k,r=0,0,1,0
        if slot==1:lo,hi,k,r=0,100,3,0
        payload=lo,hi,k,r
    elif name=="dynamic_connectivity":
        n=max(2,size);ops=[]
        for _ in range(3*size):
            op=rng.choice("++--??")
            ops.append((op,rng.randrange(n)) if op=='?' else (op,rng.randrange(n),rng.randrange(n)))
        ops.append(('?',0))
        if slot==0:n=1;ops=[('?',0),('-',0,0),('?',0)]
        if slot==1:n=3;ops=[('+',0,1),('+',1,0),('-',0,1),('?',0),('-',1,0),('?',0),('-',0,1),('?',1)]
        payload=n,ops
    elif name=="gf2_lex":
        n=size;rows=[(f'{rng.randrange(1<<n):0{n}b}',rng.randrange(2)) for _ in range(rng.randint(0,n+2))]
        if slot==0:n=3;rows=[]
        if slot==1:n=4;rows=[('1100',1),('0011',1)]
        payload=n,rows
    elif name=="grid_turns":
        n=min(size,6);m=rng.randint(1,6);costs=[[rng.randint(-5,9) for _ in range(m)] for _ in range(n)]
        grid=[''.join('#' if rng.random()<.12 else '.' for _ in range(m)) for _ in range(n)];k=rng.randint(0,5)
        if slot==0:costs=[[-3]];grid=['.'];k=0
        if slot==1:costs=[[1,2],[3,4]];grid=['..','..'];k=1
        payload=costs,grid,k
    else:raise ValueError(name)
    return serialize(name,payload),expected(name,payload)+'\n'


def stress(name):
    if name=='interval_k':return serialize(name,([(i,i+1,1) for i in range(1000)],30)), '30\n'
    if name=='xor_cost':return serialize(name,([3]+[1]*999,[(0,v,1) for v in range(1,1000)])), '3\n'
    if name=='tree_k':return serialize(name,([1]*60,[(i,i+1) for i in range(59)],30)), '30\n'
    if name=='digit_range':return serialize(name,(0,10**18-1,1,0)),str(1+sum(9**length for length in range(1,19)))+'\n'
    if name=='dynamic_connectivity':
        ops=[('+',i,i+1) for i in range(999)]+[('?',0)]+[('-',i,i+1) for i in range(999)]+[('?',0)]
        return serialize(name,(1000,ops)),'1000\n1\n'
    if name=='gf2_lex':return serialize(name,(60,[(f'{1<<i:060b}',1) for i in range(60)])),'1'*60+'\n'
    if name=='two_machines':return serialize(name,([(0,1,i) for i in range(1,1001)],0)),'1999\n'
    if name=='grid_turns':return serialize(name,([[1]*25 for _ in range(25)],['.'*25]*25,1)),'49\n'
    raise ValueError(name)


def generate():
    cohort=[]
    for family_index,(name,(statement,input_format,output_format,code)) in enumerate(SPECS.items()):
        reference=dedent(code).lstrip()
        for variant in range(4):
            base=SEED+10000*family_index+100*variant
            tests=[]
            for slot,size in enumerate((1,2,6,8,3,5,7,9,10,11,12,8)):
                stdin,stdout=case(name,base+slot,size,slot)
                tests.append({'id':('public' if slot<4 else 'reserved')+str(slot+1),'input':stdin,'output':stdout})
            stdin,stdout=stress(name);tests.append({'id':'reserved-stress','input':stdin,'output':stdout})
            task=ActorTask.from_dict(f'v3-code-{name}-{variant+1:02d}',name,{'domain':'coding',
                'statement':'Write a complete Python 3.11 program using only the standard library, reading stdin and writing stdout. Return the Python source in the code field. '+statement,
                'input_format':input_format,'output_format':output_format,'public_examples':tests[:4]})
            evaluator=EvaluatorTask.bind(task,{'private_tests':tests[4:],'reference_code':reference,'reference_sha256':digest(reference),
                'private_tests_sha256':digest(wire(tests[4:])),'seed':base,'family_cluster':name,'variant':variant+1,
                'origin':'original repository-authored coupled algorithm problem and tests; not LiveCodeBench',
                'reference_provenance':'Original program in coding_tasks.py; independent exhaustive finite oracle and analytic stress output.',
                'license':'repository-authored','retained_tests_complete':True,'independence':'four variants share one algorithmic template'})
            cohort.append((task,evaluator))
    return cohort
