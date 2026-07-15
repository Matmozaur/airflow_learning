# Airflow Learning Repository

A hands-on learning environment for Apache Airflow **3.3.0**, running locally with Docker Compose.

## Quick Start

```bash
# 1. (Linux/macOS only) Set the user ID so mounted files are owned correctly
echo "AIRFLOW_UID=$(id -u)" > .env

# 2. Initialise the database and create the admin user (runs once)
docker compose up airflow-init

# 3. Start Airflow
docker compose up -d

# 4. Open the web UI
#    http://localhost:8080   user: airflow / password: airflow
```

To stop Airflow:
```bash
docker compose down
```

To reset everything (deletes all logs and the database):
```bash
docker compose down --volumes --remove-orphans
```

## Repository Layout

```
.
├── dags/
│   ├── basics/              # Core concepts: operators, TaskFlow API, XCom
│   ├── sensors/             # File sensor and SQL sensor examples
│   └── taskflow_operations/ # Branching with operators and TaskFlow
├── datasets/                # Sample CSV data used by DAGs
├── outputs/                 # DAG output files (mounted into containers)
├── plugins/                 # Custom Airflow plugins
├── config/                  # airflow.cfg overrides
├── docs/                    # Concept documentation (start here!)
├── Dockerfile               # Custom image with extra providers
├── docker-compose.yaml      # Local dev stack (Airflow 3.3.0 + PostgreSQL 16)
└── requirements.txt         # Extra Python packages installed into the image
```

## Using a Custom Image (with extra providers)

The default `docker compose up` uses the official `apache/airflow:3.3.0` image.
If your DAGs need the Postgres operator or the SQL sensor, build the custom image:

```bash
# In docker-compose.yaml, comment "image:" and uncomment "build: ."
docker compose build
docker compose up airflow-init
docker compose up -d
```

## Documentation

| File | Topic |
|------|-------|
| [docs/01_core_concepts.md](docs/01_core_concepts.md) | DAGs, tasks, operators, scheduler |
| [docs/02_operators_and_taskflow.md](docs/02_operators_and_taskflow.md) | Operators vs TaskFlow API |
| [docs/03_xcoms_data_passing.md](docs/03_xcoms_data_passing.md) | Passing data between tasks with XCom |
| [docs/04_sensors.md](docs/04_sensors.md) | Sensors and deferrable operators |
| [docs/05_branching.md](docs/05_branching.md) | Conditional execution / branching |

## DAG Examples

| DAG ID | File | What it demonstrates |
|--------|------|----------------------|
| `dag_with_operators` | `basics/dag_with_operators.py` | Task dependency graph with PythonOperator |
| `dag_with_taskflow` | `basics/dag_with_taskflow.py` | Same graph using the TaskFlow API |
| `example_dag` | `basics/example_dag.py` | Minimal DAG with EmptyOperator |
| `cross_task_communication_operators` | `basics/passing_data_with_operators.py` | XCom push/pull with operators |
| `cross_task_communication_taskflow` | `basics/passing_data_with_taskflow.py` | XCom via TaskFlow return values |
| `cross_task_communication_taskflow_mo` | `basics/passing_data_with_taskflow_multiple_outputs.py` | `multiple_outputs=True` |
| `simple_file_sensor` | `sensors/simple_file_sensor.py` | FileSensor waiting for a CSV |
| `pipeline_with_sql_sensor` | `sensors/pipeline_with_sql_sensor.py` | SqlSensor with Postgres |
| `branching_using_operators` | `taskflow_operations/branching_using_operators.py` | BranchPythonOperator |
| `branching_using_taskflow` | `taskflow_operations/branching_using_taskflow.py` | `@task.branch` decorator |

## Airflow 3.x Migration Notes

This repo was upgraded from Airflow 2.9 to **3.3.0**. Key breaking changes handled:

| Old (2.x) | New (3.x) |
|-----------|-----------|
| `airflow.operators.dummy_operator.DummyOperator` | `airflow.operators.empty.EmptyOperator` |
| `airflow.operators.python_operator.PythonOperator` | `airflow.operators.python.PythonOperator` |
| `airflow.sensors.sql_sensor.SqlSensor` | `airflow.providers.common.sql.sensors.sql.SqlSensor` |
| `airflow.utils.dates.days_ago` | `datetime(2024, 1, 1)` (fixed date) |
| `schedule_interval='...'` | `schedule='...'` |
| CeleryExecutor (docker-compose) | **LocalExecutor** (simpler for local dev) |
| `AIRFLOW__API__AUTH_BACKENDS` | `AIRFLOW__CORE__AUTH_MANAGER` |
| `postgres:13` | `postgres:16` |
