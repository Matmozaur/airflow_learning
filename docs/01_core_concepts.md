# Core Airflow Concepts

## What is Apache Airflow?

Apache Airflow is an open-source platform for **programmatically authoring, scheduling, and monitoring workflows**. Workflows are defined as Python code, making them versionable, testable, and maintainable like any other software.

---

## DAG (Directed Acyclic Graph)

A **DAG** is the central concept in Airflow. It defines:
- **What** tasks to run
- **In what order** (dependencies)
- **How often** (schedule)

```
start ──► task_a ──► task_c ──► end
          task_b ──►
```

Key DAG parameters:

| Parameter | Purpose | Example |
|-----------|---------|---------|
| `dag_id` | Unique identifier | `'my_pipeline'` |
| `start_date` | First possible run date | `datetime(2024, 1, 1)` |
| `schedule` | Cron or preset | `'@daily'`, `'0 6 * * *'` |
| `catchup` | Run missed intervals? | `False` (recommended for learning) |
| `tags` | UI labels | `['etl', 'postgres']` |
| `default_args` | Defaults applied to all tasks | `{'retries': 2}` |

### Schedule Presets

| Preset | Equivalent cron | Meaning |
|--------|-----------------|---------|
| `@once` | — | Run exactly once |
| `@hourly` | `0 * * * *` | Every hour |
| `@daily` | `0 0 * * *` | Daily at midnight |
| `@weekly` | `0 0 * * 0` | Weekly on Sunday |
| `@monthly` | `0 0 1 * *` | First day of the month |
| `@continuous` | — | Re-run as soon as previous run ends |
| `None` | — | Manual trigger only |

> **Airflow 3.x note:** The `schedule_interval` parameter was removed. Use `schedule` instead.

---

## Tasks

A **task** is a single unit of work inside a DAG. Every task has:
- A unique `task_id` within the DAG
- An **operator** that defines what the task does
- Optional **retry** and **timeout** settings

### Task States

| State | Meaning |
|-------|---------|
| `queued` | Waiting for a worker slot |
| `running` | Currently executing |
| `success` | Completed successfully |
| `failed` | Raised an exception |
| `skipped` | Intentionally skipped (e.g., branching) |
| `upstream_failed` | A dependency failed |

---

## Operators

An **operator** is a template that defines a single task. Airflow ships with hundreds of built-in operators:

| Operator | Module | Purpose |
|----------|--------|---------|
| `PythonOperator` | `airflow.operators.python` | Run a Python function |
| `BashOperator` | `airflow.operators.bash` | Run a shell command |
| `EmptyOperator` | `airflow.operators.empty` | No-op placeholder (was `DummyOperator`) |
| `BranchPythonOperator` | `airflow.operators.python` | Conditional branching |
| `PostgresOperator` | `airflow.providers.postgres.operators.postgres` | Execute SQL on Postgres |

See [02_operators_and_taskflow.md](02_operators_and_taskflow.md) for a full comparison.

---

## Task Dependencies

Dependencies are set with the **bit-shift operators** `>>` and `<<`:

```python
# Linear chain
task_a >> task_b >> task_c

# Fan-out (parallel)
task_a >> [task_b, task_c]

# Fan-in
[task_b, task_c] >> task_d

# Mixed
[task_a, task_b] >> task_e
[task_c, task_d] >> task_f
[task_e, task_f] >> task_g
```

---

## The Scheduler

The **scheduler** is the Airflow component that:
1. Parses DAG files at regular intervals
2. Decides which DAG runs are due based on `schedule` and `start_date`
3. Submits ready tasks to the executor

### Executors

The **executor** determines *how* tasks are run:

| Executor | Use case |
|----------|----------|
| `LocalExecutor` | Local dev, runs tasks as sub-processes |
| `CeleryExecutor` | Distributed, horizontally scalable |
| `KubernetesExecutor` | Runs each task in a Kubernetes pod |

> This repo uses **LocalExecutor** — the simplest option for learning.

---

## DAG Runs vs Task Instances

- A **DAG Run** is a single execution of a DAG for a specific logical date (`data_interval_start`).
- A **Task Instance** is one execution of one task within a DAG Run.

Both are stored in the metadata database and visible in the Airflow UI.

---

## Key Files in This Repo

| File | What to read |
|------|-------------|
| `dags/basics/example_dag.py` | Minimal DAG with EmptyOperator |
| `dags/basics/dag_with_operators.py` | Multi-task dependency graph |
| `dags/basics/dag_with_taskflow.py` | Same graph with the TaskFlow API |
