"""Make the evaluator's Python 3.11 language contract explicit in every actor task."""
from ..cohort_v1.authored import generate as original
from ..records import ActorTask, EvaluatorTask

LANGUAGE = "Write a complete Python 3.11 program using only its standard library. Read stdin and write stdout. Return the Python source in the code field. "


def generate():
    result=[]
    for task,evaluator in original():
        public=task.data()
        public["statement"]=LANGUAGE+public["statement"]
        actor=ActorTask.from_dict(task.task_id,task.stratum,public)
        material=evaluator.data()
        material["language_amendment"]={"actor_language":"Python 3.11 standard library", "reason":"Version 1 omitted the execution language; model-selected C++ was rejected by the Python grader.",
                                        "cohort_relation":"same tasks and exact retained tests; post-observation engineering retest, not independent confirmation"}
        result.append((actor,EvaluatorTask.bind(actor,material)))
    return result
