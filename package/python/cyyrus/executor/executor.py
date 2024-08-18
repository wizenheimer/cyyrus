# cyyrus/executor/executor.py
# TODO: implement async task executor


from typing import Any, Dict, List


class Executor:

    def __init__(self):
        pass

    def execute(
        self,
        task_id: str,
        task_model: Any,
        task_inputs: List[Dict[str, Any]],
        task_properties: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        # TODO: infer the task based on the task_id
        # TODO: create the task object using task_properties
        # TODO: iterate over task_inputs and execute the task one by one
        # TODO: execute the task
        return []
