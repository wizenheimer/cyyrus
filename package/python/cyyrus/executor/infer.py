from collections import defaultdict
import importlib
import inspect


def infer_tasks():
    try:
        module = importlib.import_module("cyyrus.tasks")
    except ImportError:
        # log.warning("No tasks found")
        print("No tasks found")
    else:
        from cyyrus.tasks.base import BaseTask
        from cyyrus.tasks.default import DefaultTask

        task_dict = defaultdict(lambda: DefaultTask)

        for _, cls in inspect.getmembers(module, inspect.isclass):
            if (hasattr(cls, "TASK_ID") and issubclass(cls, BaseTask)) and cls != BaseTask:
                task_dict[cls.TASK_ID] = cls  # type: ignore

        return task_dict
