# Sensors

## What is a Sensor?

A **sensor** is a special type of operator that **waits** for a condition to become true before allowing the pipeline to proceed. Common use cases:

- Wait for a file to appear on a filesystem
- Wait for a record to appear in a database table
- Wait for an HTTP endpoint to return a specific status
- Wait for a cloud storage object to be created

Sensors periodically check the condition (poke) and either proceed or keep waiting.

---

## Key Sensor Parameters

| Parameter | Purpose | Default |
|-----------|---------|---------|
| `poke_interval` | Seconds between condition checks | `60` |
| `timeout` | Max seconds to wait before failing | `7 * 24 * 3600` (7 days) |
| `mode` | `'poke'` (blocking) or `'reschedule'` (frees the worker slot between checks) | `'poke'` |
| `soft_fail` | Mark as `skipped` instead of `failed` on timeout | `False` |
| `deferrable` | Use the Triggerer service instead of polling (Airflow 2.2+) | `False` |

> **Best practice:** Prefer `deferrable=True` in Airflow 2.2+ (requires the Triggerer service). Fall back to `mode='reschedule'` when a deferrable version is not available, to avoid occupying a worker slot while waiting.

---

## FileSensor

`FileSensor` waits until a file or directory exists at the given path.

```python
from airflow.sensors.filesystem import FileSensor

wait_for_csv = FileSensor(
    task_id='wait_for_csv',
    filepath='/opt/airflow/datasets/sensor_target.csv',
    poke_interval=10,      # check every 10 seconds
    timeout=60 * 10,       # give up after 10 minutes
    mode='reschedule',     # don't hold a worker slot while waiting
)
```

> The file path is evaluated inside the container. Mount the host directory into the container via `docker compose` volumes.

---

## SqlSensor

`SqlSensor` executes a SQL query and proceeds when the query returns a truthy result (a non-empty, non-zero result set).

`SqlSensor` was moved to the `common-sql` provider package (`apache-airflow-providers-common-sql`) in Airflow 2.x. Import it from the provider:

```python
from airflow.providers.common.sql.sensors.sql import SqlSensor

wait_for_data = SqlSensor(
    task_id='wait_for_data',
    conn_id='postgres_connection_laptop_db',   # Airflow connection ID
    sql="SELECT EXISTS(SELECT 1 FROM laptops WHERE price_euros > 500)",
    poke_interval=10,
    timeout=10 * 60,
    mode='reschedule',
)
```

---

## Deferrable Operators (Airflow 2.2+)

Standard sensors with `mode='poke'` block a worker slot for the entire wait duration. **Deferrable sensors** go further: they suspend themselves entirely and are resumed by the **Triggerer** component when the condition is met, freeing the worker slot completely.

This is the preferred approach for long-running waits in Airflow 2.2+.

```python
from airflow.sensors.filesystem import FileSensor

# Deferrable version — requires the Triggerer service to be running
wait_for_csv = FileSensor(
    task_id='wait_for_csv',
    filepath='/opt/airflow/datasets/sensor_target.csv',
    deferrable=True,          # suspend task; wake it up via Triggerer
    poke_interval=10,         # how often the Triggerer re-checks
)
```

> Not all sensors support `deferrable=True`. Check the provider's changelog. The `airflow-triggerer` service in this repo's `docker-compose.yaml` enables deferrable operators.

---

## Sensor vs. External Trigger

| Approach | When to use |
|----------|------------|
| **Sensor** (`poke` / `reschedule`) | Short-to-medium waits; condition is within Airflow's reach |
| **Deferrable sensor** | Long waits; requires the Triggerer service |
| **ExternalTaskSensor** | Waiting for another Airflow DAG / task to complete |
| **Dataset / Asset trigger** (Airflow 2.4+) | Data-aware scheduling; a DAG runs when an upstream DAG produces a named asset |
| **External trigger** (REST API / CLI) | When the upstream system can call Airflow directly to trigger a DAG run |

---

## Example Pipeline with SqlSensor

```
[create_laptops_table, create_premium_laptops_table]
         ↓
 wait_for_premium_laptops   ← SqlSensor polls until rows with price > 500 exist
         ↓
 insert_data_into_premium_laptops_table
         ↓
 delete_laptop_data
```

---

## Examples in This Repo

| DAG | Sensor used |
|-----|-------------|
| `dags/sensors/simple_file_sensor.py` | `FileSensor` |
| `dags/sensors/pipeline_with_sql_sensor.py` | `SqlSensor` + `PostgresOperator` |
