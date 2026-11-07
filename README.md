# Cloud Capacity Planner

**Cloud / reliability engineering** · A queueing-theory capacity planner and seeded discrete-event simulation.

## Run locally

Python 3.11+; no third-party packages required. From the standalone repository checkout root:

```bash
python main.py demo
python main.py run example.json
python -m unittest discover -s tests -v
```

`example.json` is the input contract and contains only synthetic or fictional data. `core.run(payload)` returns a JSON-serializable result. Invalid inputs produce an error and a nonzero CLI exit code.

## What it implements

- Erlang-C wait probability, utilization and expected response for stable M/M/c queues.
- Searches worker counts against a target probability of waiting beyond an SLO threshold.
- Seeded heap-based simulation estimates queue wait, response percentiles and completed jobs.
- Reports hourly cost from user-supplied rates, with unstable capacity rejected.

## Design and limitations

Assumes Poisson arrivals, independent exponential service times and identical workers. Costs are inputs, not live cloud prices. Simulated percentiles are estimates with finite-sample variation; no startup/transient correction or confidence intervals are included. This tool does not provision cloud resources or incur cloud charges.

## Suggested next step

Add your own data and domain-specific acceptance tests. Read and understand the implementation before presenting it in interviews. No live deployment is implied.

<!-- AH-INDEPTH-DOCS:START -->
## In-depth engineering guide

### Problem and scope

A queueing-theory capacity planner and seeded discrete-event simulation.

This is an independent runnable reference implementation, with synthetic sample input and explicit limits. It is not a deployed service or independently validated business result.

### Architecture and end-to-end flow

```text
Arrival/service/SLO inputs → Erlang-C worker search → user-supplied hourly-cost estimate → seeded discrete-event simulation
```

| File | Responsibility |
|---|---|
| core.py | Domain validation and project-specific algorithm/state transitions |
| main.py | Bounded JSON CLI input, demo dispatch and JSON output |
| example.json | Exact reproducible sample input |
| tests/test_core.py | Unit and edge-case coverage |

### Design decisions and trade-offs

1. The analytic model is M/M/c: Poisson arrivals, exponential service and homogeneous parallel workers. Stability requires offered traffic below total service capacity.

2. Erlang-C predicts waiting probability and an SLO wait-breach probability. The discrete-event simulation provides a seeded empirical comparison, including p95 waiting and response time.

3. Costs use the rate supplied by the caller, not live cloud pricing. There is no autoscaler, provider integration, deployment or billing action. Real workloads may violate queueing assumptions.

### Reproducible setup

Requires Python 3.11+ and no third-party Python packages. Run from the standalone repository checkout root:

```bash
python main.py demo
python main.py run example.json
python -m unittest discover -s tests -v
```

CLI inputs are JSON objects, bounded to 1 MB. Supported domain errors produce a JSON error on stderr and a nonzero exit; inspect the message rather than treating a failed run as a result. The demo does not require a model key, network access or production data.

### Exact example input

```json
{
  "arrival_per_second": 8,
  "service_per_worker_second": 3,
  "max_wait_seconds": 0.5,
  "max_wait_breach_probability": 0.05,
  "hourly_cost_per_worker": 0.04,
  "simulation_jobs": 5000,
  "seed": 42
}
```

### Core implementation interfaces

| Callable | Boundary |
|---|---|
| `erlang(arrival, service, c)` | Implementation boundary; see source for validation and return structure. |
| `percentile(values, q)` | Implementation boundary; see source for validation and return structure. |
| `simulate(arrival, service, c, jobs, seed)` | Implementation boundary; see source for validation and return structure. |
| `run(p)` | Implementation boundary; see source for validation and return structure. |

The Python `run` result is JSON-serializable. Inspect the source and `main.py run example.json` output for the exact return keys; do not assume another project’s result schema.

### Test coverage and reproducibility

- `tests/test_core.py::test_mm1`
- `tests/test_core.py::test_unstable`
- `tests/test_core.py::test_slo`
- `tests/test_core.py::test_repeat`
- `tests/test_core.py::test_bad_rate`

5 named tests are present in this repository. Run the standalone unittest command above; it includes local HTTP tests where present. The GitHub Actions workflow supports pull requests and manual dispatch; remote CI has not been run as part of this preparation. Docker build/run was not executed; no real cloud/model/production-cluster validation is claimed.

### Security and failure boundaries

Assumes Poisson arrivals, independent exponential service times and identical workers. Costs are inputs, not live cloud prices. Simulated percentiles are estimates with finite-sample variation; no startup/transient correction or confidence intervals are included. This tool does not provision cloud resources or incur cloud charges.

Never commit .env, real API keys, runtime databases, approval material or customer data. See SECURITY.md. A successful example demonstrates the included workflow, not safe internet deployment.

### Troubleshooting

- **Import error:** run from this project’s own folder; each project intentionally has its own core.py.
- **Invalid sample/schema:** start from example.json, then change one field at a time and read the returned validation message.
- **Port already in use:** stop the previous process or select another --port where server.py exists.
- **SQLite lock/state surprise:** close duplicate processes, confirm PROJECT_DB and back up before deliberate resets. Do not delete unrelated project data.
- **External dependency unavailable:** default demos run offline; live provider calls and container pulls require your own working access and may incur external costs.

### Known limitations

Assumes Poisson arrivals, independent exponential service times and identical workers. Costs are inputs, not live cloud prices. Simulated percentiles are estimates with finite-sample variation; no startup/transient correction or confidence intervals are included. This tool does not provision cloud resources or incur cloud charges.

### Extension roadmap — not implemented

Validate arrival/service distributions, model nonstationary bursts, add sensitivity intervals and account for provider-specific minimums, cold starts and operational overhead.
<!-- AH-INDEPTH-DOCS:END -->


## Provenance and standalone layout

Extracted from `applied-ai-engineering-lab/projects/10-cloud-capacity-planner`. The algorithms, CLI, tests, examples and any server/UI/worker/Docker files are retained byte-for-byte. Only documentation, repository hygiene and CI configuration were adapted for standalone use. This checkout needs neither the parent collection catalog nor its runner/publisher. It is a reference implementation, not evidence of a historical production deployment or measured business outcome.
