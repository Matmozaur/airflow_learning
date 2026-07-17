# Operators vs the TaskFlow API

Airflow provides two styles for defining tasks. Both are first-class citizens — choose the one that fits your use case.

> **Airflow version note:** This repo uses Airflow 2.x/3.x conventions. The `schedule` parameter (not the deprecated `schedule_interval`) is used throughout. `provide_context=True` is no longer needed and was removed in Airflow 3.x.

---

## Traditional Operators

The classic style wraps every task in an explicit **operator**. This style is still fully supported in Airflow 2.x and 3.x — it is not "legacy", just more verbose than the TaskFlow API.

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime

def greet():
    print("Hello from an operator!")

with DAG(
    dag_id='operators_demo',
    start_date=datetime(2024, 1, 1),
    schedule='@once',
    catchup=False,          # best practice: avoid backfill runs
) as dag:
    greet_task = PythonOperator(
        task_id='greet',
        python_callable=greet,
    )
```

### Passing Data Between Operator Tasks (XCom)

Operators communicate via **XCom** — a key/value store in the metadata database. Access the `TaskInstance` through the function's `context` dict (automatically injected by Airflow 2.x+; no `provide_context=True` needed).

```python
def push_data(**context):
    context['ti'].xcom_push(key='my_key', value=42)

def pull_data(**context):
    value = context['ti'].xcom_pull(task_ids='push_task', key='my_key')
    print(f"Got: {value}")
```

See [03_xcoms_data_passing.md](03_xcoms_data_passing.md) for a full walkthrough.

---

## TaskFlow API (`@task` decorator)

Introduced in Airflow 2.0, the **TaskFlow API** removes boilerplate: return values are automatically pushed as XComs and pulled by downstream tasks. This is the **recommended style** for pure-Python pipelines.

```python
from airflow.decorators import dag, task
from datetime import datetime

@dag(
    dag_id='taskflow_demo',
    start_date=datetime(2024, 1, 1),
    schedule='@once',
    catchup=False,
)
def my_pipeline():

    @task
    def get_number() -> int:
        return 42

    @task
    def double(n: int) -> int:
        return n * 2

    @task
    def display(n: int):
        print(f"Result: {n}")

    display(double(get_number()))

my_pipeline()
```

### `multiple_outputs=True`

When a task returns a **dict** and downstream tasks need to consume individual keys as separate XComs, set `multiple_outputs=True`.

> **Tip:** Airflow also infers `multiple_outputs=True` automatically when the return type annotation is `dict[str, ...]`. The explicit parameter is clearer and recommended.

```python
@task(multiple_outputs=True)
def compute_stats(values: list) -> dict:
    return {
        'total': sum(values),
        'average': sum(values) / len(values),
    }

stats = compute_stats([1, 2, 3, 4, 5])
# Each key becomes a separate XCom entry:
# stats['total'] and stats['average'] can be wired to different downstream tasks
```

---

## Side-by-Side Comparison

| Feature | Traditional Operators | TaskFlow API |
|---------|----------------------|--------------|
| Syntax verbosity | Higher (explicit `PythonOperator`) | Lower (`@task` decorator) |
| XCom push/pull | Manual (`ti.xcom_push / xcom_pull`) | Automatic (return values) |
| Type hints | Not enforced | Supported, improves readability |
| Mixing styles | ✅ Supported | ✅ Can mix with operators |
| Branching | `BranchPythonOperator` | `@task.branch` |
| Non-Python tasks | `BashOperator`, `PostgresOperator`, etc. | Use operator directly |
| Context access | `**context` / `**kwargs` | `get_current_context()` or `**kwargs` |

### When to use each

- **TaskFlow API** — pure Python pipelines where tasks pass data to each other. Much less boilerplate; the recommended default.
- **Traditional operators** — integrations with external systems (`PostgresOperator`, `S3CopyObjectOperator`, `SparkSubmitOperator`, …), or when you need precise control over XCom keys.
- **Both styles can coexist** in the same DAG — there is no penalty for mixing them.

---

## Mixing Both Styles

You can freely mix operators and `@task` functions in the same DAG:

```python
from airflow.decorators import dag, task
from airflow.operators.bash import BashOperator
from datetime import datetime

@dag(start_date=datetime(2024, 1, 1), schedule='@once', catchup=False)
def mixed_pipeline():

    @task
    def prepare() -> str:
        return "hello"

    bash_task = BashOperator(task_id='run_script', bash_command='echo "Running bash step"')

    @task
    def finish(msg: str):
        print(f"Done: {msg}")

    msg = prepare()
    bash_task >> finish(msg)   # operator and @task can be chained with >>

mixed_pipeline()
```

---

## Airflow 3.x Notes

| Change | Detail |
|--------|--------|
| `schedule_interval` | **Removed.** Use `schedule` instead. |
| `provide_context` | **Removed.** Context is always injected via `**kwargs` / `**context`. |
| `DummyOperator` | **Removed.** Use `EmptyOperator` from `airflow.operators.empty`. |
| Task SDK | Airflow 3.x ships a standalone `apache-airflow-task-sdk` package; `@task` decorated functions can run outside the scheduler process. |
| `Dataset` → `Asset` | Data-aware scheduling now uses `Asset` (and `AssetAlias`). |

---

## Examples in This Repo

| DAG | Style |
|-----|-------|
| `dags/basics/dag_with_operators.py` | Traditional operators |
| `dags/basics/dag_with_taskflow.py` | TaskFlow API |
| `dags/basics/passing_data_with_operators.py` | XCom with operators |
| `dags/basics/passing_data_with_taskflow.py` | XCom with TaskFlow |
| `dags/basics/passing_data_with_taskflow_multiple_outputs.py` | `multiple_outputs=True` |
