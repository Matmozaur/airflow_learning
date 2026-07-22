# Branching

## What is Branching?

**Branching** lets a DAG take different execution paths based on runtime conditions. Instead of always running all tasks, you can choose which branch to follow (e.g., based on a variable, the current date, or data characteristics).

---

## BranchPythonOperator

The `BranchPythonOperator` calls a Python function that **returns a `task_id` or a list of `task_id`s to execute next**. All other downstream tasks are marked as **skipped**.

```python
from airflow.operators.python import BranchPythonOperator
from airflow.models import Variable

def choose_branch():
    # Any logic here — query a DB, check a Variable, inspect data...
    mode = Variable.get("transform", default_var="filter_a")
    if mode == "filter_a":
        return "filter_a_task"
    return "filter_b_task"
    # Return a list to execute multiple branches: return ["filter_a_task", "notify_task"]

branch_task = BranchPythonOperator(
    task_id="choose_branch",
    python_callable=choose_branch,
)
```

---

## `@task.branch` (TaskFlow API)

The `@task.branch` decorator is the TaskFlow equivalent. It returns a `task_id` string (or a list of `task_id` strings) to activate:

```python
from airflow.decorators import dag, task
from airflow.models import Variable
from datetime import datetime

@dag(start_date=datetime(2024, 1, 1), schedule='@once', catchup=False)
def branching_pipeline():

    @task.branch
    def decide() -> str:
        mode = Variable.get("transform", default_var="path_a")
        return "path_a_task" if mode == "path_a" else "path_b_task"

    @task(task_id="path_a_task")
    def path_a():
        print("Taking path A")

    @task(task_id="path_b_task")
    def path_b():
        print("Taking path B")

    @task(trigger_rule="none_failed_min_one_success")
    def finish():
        print("Pipeline finished")

    decide() >> [path_a(), path_b()] >> finish()

branching_pipeline()
```

---

## `trigger_rule` — Controlling When a Task Runs

By default, a task runs only if **all upstream tasks succeeded**. Branching skips some tasks, so the downstream "merge" task needs a different rule:

| `trigger_rule` | Behaviour |
|----------------|-----------|
| `all_success` *(default)* | Run only if **all** upstreams succeeded |
| `none_failed` | Run if **no** upstream failed (skipped counts as OK) |
| `none_failed_min_one_success` | No upstream failed **and** at least one succeeded ✅ best fit for branching merge |
| `one_success` | Run as soon as **one** upstream succeeds |
| `all_done` | Run when **all** upstreams are done (any state) |
| `always` | Run unconditionally |

> **Which rule to use after branching?**
> - Use `none_failed_min_one_success` for the merge task — it ensures the pipeline only continues when a branch actually ran, not just because nothing failed.
> - `none_failed` also works but is more permissive: the merge task would run even if every upstream was skipped.

```python
# The merge task must tolerate skipped branches
finish_task = PythonOperator(
    task_id="finish",
    python_callable=cleanup,
    trigger_rule="none_failed_min_one_success",   # ← correct rule after branching
)
```

---

## Airflow Variables

Both branching examples in this repo use `airflow.models.Variable` to control which branch runs at runtime — without redeploying code.

### Set a variable via the CLI:
```bash
docker exec -it <webserver_container> airflow variables set transform filter_two_seaters
# or:
docker exec -it <webserver_container> airflow variables set transform filter_fwds
```

### Set a variable via the UI:
1. Open the Airflow UI → **Admin → Variables**
2. Click **+** and add `transform` = `filter_two_seaters`

### Access in a DAG:
```python
from airflow.models import Variable

value = Variable.get("transform", default_var="filter_two_seaters")
```

---

## Example: CSV Transformation Pipeline

```
read_csv_file_task
       ↓
determine_branch_task   ← reads the "transform" Variable
      ↙         ↘
filter_two_seaters   filter_fwds
      ↘         ↙
  write_csv_result_task  (trigger_rule="none_failed")
```

---

## Examples in This Repo

| DAG | Style |
|-----|-------|
| `dags/taskflow_operations/branching_using_operators.py` | `BranchPythonOperator` |
| `dags/taskflow_operations/branching_using_taskflow.py` | `@task.branch` |
