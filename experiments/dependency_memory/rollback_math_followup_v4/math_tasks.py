"""New planted finite tasks with explicitly scalar outputs and independent checks."""
import random

from ..rollback_pilot.records import ActorTask, EvaluatorTask

BASE_SEED=2026100851


def generate():
    tasks=[]
    for family,count in (("integer",8),("modular",8),("coloring",16)):
        for index in range(count):
            seed=BASE_SEED+1000*(1+("integer","modular","coloring").index(family))+index
            rng=random.Random(seed)
            if family=="coloring":
                n=12 if index<8 else 14
                witness=[rng.randrange(4) for _ in range(n)]
                allowed=[[c,rng.choice([x for x in range(4) if x!=c])] for c in witness]
                for colors in allowed:rng.shuffle(colors)
                edges=[[a,b] for a in range(n) for b in range(a+1,n) if witness[a]!=witness[b] and rng.random()<.6]
                constraints=[]; high=3
            else:
                n=5 if family=="integer" or index>=4 else 4
                high=7 if family=="modular" else 9
                witness=[rng.randint(0,high) for _ in range(n)]
                constraints=[]
                for row in range(n-1):
                    coefficients=[rng.randint(-5,5) for _ in range(n)]
                    if not any(coefficients):coefficients[row]=1
                    total=sum(a*b for a,b in zip(coefficients,witness))
                    item={"id":f"q{row+1}","coefficients":coefficients}
                    if family=="integer":item["equals"]=total
                    else:
                        modulus=rng.choice((7,11,13));item.update(modulus=modulus,residue=total%modulus)
                    constraints.append(item)
                allowed=None;edges=[]
            public={"domain":"math","statement":"Return one integer per variable in declared order as {\"values\":[...]}. Each value must satisfy the public bounds and every constraint. For list coloring, choose ONE SCALAR color from each vertex's allowed list; the lists themselves are not colors and must not be encoded as new color numbers.",
                    "family":family,"variables":[f"v{i+1}" for i in range(n)],"bounds":{"minimum":0,"maximum":high},
                    "constraints":constraints,"allowed_colors":allowed,"edges":edges}
            task=ActorTask.from_dict(f"v4-math-{family}-{index+1:02d}",family,public)
            evaluator=EvaluatorTask.bind(task,{"witness":{"values":witness},"seed":seed,"origin":"new repository-authored planted finite task",
                                              "family_cluster":family,"license":"repository-authored","development_cohort":"mathematical follow-up v4"})
            tasks.append((task,evaluator))
    return tasks
