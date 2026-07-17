# Passing Data Between Tasks — XCom

## What is XCom?

**XCom** (cross-communication) is Airflow's mechanism for passing small amounts of data between tasks. XComs are stored in the metadata database and are accessible via the Airflow UI under **Admin → XComs**.

> **Caution:** XComs are meant for *small* values (IDs, file paths, short strings, small dicts). Large payloads (DataFrames, binary blobs) should be written to external storage (S3, GCS, a database) and only the *location* passed via XCom. A rough rule of thumb: keep individual XCom values under a few KB.

---

## XCom with Traditional Operators

### Pushing a value

In Airflow 2.x+, the task context (including the `TaskInstance` as `ti`) is **automatically injected** into any Python callable via `**kwargs` or `**context`. No `provide_context=True` is needed (that parameter was deprecated in 2.x and removed in 3.x).

```python
def push_order_data(**context):
    ti = context['ti']                        # TaskInstance
    data = {'o1': 234.45, 'o2': 10.00}
    ti.xcom_push(key='order_data', value=data)
```

### Pulling a value

```python
def pull_order_data(**context):
    ti = context['ti']
    data = ti.xcom_pull(task_ids='push_order_data', key='order_data')
    print(data)
```

### Automatic return-value XCom

A Python function's **return value** is automatically pushed as XCom with `key='return_value'`:

```python
def get_value():
    return 42   # pushed automatically as key='return_value'

def use_value(**context):
    val = context['ti'].xcom_pull(task_ids='get_value_task')  # key defaults to 'return_value'
    print(val)
```

---

## XCom with the TaskFlow API

The TaskFlow API eliminates the need for explicit `xcom_push` / `xcom_pull`. Return values flow automatically:

```python
from airflow.decorators import dag, task
from datetime import datetime

@dag(start_date=datetime(2024, 1, 1), schedule='@once', catchup=False)
def order_pipeline():

    @task
    def get_orders() -> dict:
        return {'o1': 234.45, 'o2': 10.00, 'o3': 34.77}

    @task
    def compute_total(orders: dict) -> float:
        return sum(orders.values())

    @task
    def display(total: float):
        print(f"Total: {total:.2f}")

    display(compute_total(get_orders()))

order_pipeline()
```

Under the hood, each `@task` result is stored in XCom. The wiring (which task's XCom is passed where) is inferred from the Python call graph.

---

## `multiple_outputs=True`

When a `@task` returns a `dict` and downstream tasks need to consume individual keys as separate XComs, use `multiple_outputs=True`.

> **Tip:** Airflow also infers `multiple_outputs=True` when the return type annotation is `dict[str, ...]`. The explicit parameter is clearer and recommended.

```python
@task(multiple_outputs=True)
def compute_stats(orders: dict) -> dict:
    total = sum(orders.values())
    average = total / len(orders)
    return {'total': total, 'average': average}

stats = compute_stats(orders)
# Each key becomes a separate XCom entry:
# stats['total'] and stats['average'] can be wired to different downstream tasks
```

---

## XCom Limitations

| Concern | Detail |
|---------|--------|
| **Size** | Stored in the metadata DB; keep payloads small (ideally < 48 KB for SQLite, < 1 MB for Postgres) |
| **Type** | Must be JSON-serialisable by default (strings, numbers, lists, dicts) |
| **Security** | XCom values are visible to all users in the Airflow UI |
| **Cross-DAG** | Supported (`ti.xcom_pull(dag_id=...)`) but not recommended; use a shared data store instead |
| **Clearing tasks** | Clearing a task also clears its XCom values |

---

## XCom Backend (Advanced)

For larger payloads, Airflow supports custom **XCom backends** that store data in S3, GCS, or other object stores while only keeping a reference in the metadata DB.

Configure in `airflow.cfg`:

```ini
[core]
xcom_backend = airflow.providers.amazon.aws.xcom_backends.s3.S3XComBackend
```

Or via the environment variable:

```bash
AIRFLOW__CORE__XCOM_BACKEND=airflow.providers.amazon.aws.xcom_backends.s3.S3XComBackend
```

The provider packages (`apache-airflow-providers-amazon`, `apache-airflow-providers-google`, etc.) ship their own XCom backend implementations.

---

## Examples in This Repo

| DAG | Topic |
|-----|-------|
| `dags/basics/passing_data_with_operators.py` | Manual `xcom_push` / `xcom_pull` |
| `dags/basics/passing_data_with_taskflow.py` | Automatic XCom via return values |
| `dags/basics/passing_data_with_taskflow_multiple_outputs.py` | `multiple_outputs=True` |
