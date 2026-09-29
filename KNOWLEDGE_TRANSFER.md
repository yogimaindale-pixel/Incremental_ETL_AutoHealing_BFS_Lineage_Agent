# Incremental ETL Auto-Healing BFS Lineage Agent - Junior Developer Knowledge Transfer (KT)

Welcome to the **Auto-Healing BFS Lineage Platform Onboarding Manual**. This guide is written specifically for junior data engineers and software developers to help you understand the architecture, explore the code, and run interactive failure scenarios locally.

---

## 1. Directory Structure & File Sitemap

```
src/
├── common/             # Common models, logging, exceptions, security, & config
│   ├── models.py       # Pydantic schemas (Incident, LineageNode, FailureEvent)
│   ├── logging.py      # JSON structured logger
│   └── exceptions.py   # Custom domain exception classes
├── lineage/            # Directed Graph & BFS Traversal Engine
│   ├── graph_model.py  # NetworkX graph wrapper
│   ├── bfs_traversal.py# Cycle-safe BFS upstream & downstream traversal
│   └── impact_analyzer.py # Downstream blast radius calculator
├── diagnosis/          # Failure Classification & Root Cause Engine
│   ├── signature_classifier.py # Regex rule matcher for error messages
│   └── root_cause_engine.py    # Probability scoring for candidate root causes
├── healing/            # Auto-Healing Runbooks & Rollback Circuit Breaker
│   ├── runbook_registry.py    # Execution actions for 10 runbooks
│   └── rollback.py            # Automatic rollback coordinator
└── orchestration/      # State Machine & Pipeline Coordinator
    ├── state_machine.py# 14-state transition engine with audit logging
    └── coordinator.py  # Master incident lifecycle orchestrator
```

---

## 2. Core Concepts Explained simply

### A. What is BFS Lineage Traversal?
Data flows through pipelines like rivers:
`Raw CSV File` ──► `Extract Task` ──► `Staging Table` ──► `Fact Table` ──► `Sales Report`

When an error happens at `Extract Task`, Breadth-First Search (BFS) explores:
1. **Upstream (What caused this?)**: Checks incoming edges to find if the raw CSV file was missing or corrupt.
2. **Downstream (What is affected?)**: Checks outgoing edges to calculate the blast radius on `Fact Table` and `Sales Report`.

### B. Cycle Safety in Graphs
In real enterprise platforms, data pipelines sometimes have circular references (e.g. Table A updates Table B which triggers updates back to Table A).
Our BFS algorithm tracks a `visited: Set[str]` so it **never gets stuck in an infinite loop**.

### C. Circuit Breaker & Rollback
If an auto-healing runbook executes but fails post-remediation validation checks, the system instantly triggers an automatic **Rollback** to restore the previous database watermark and prevent corrupted data from reaching production reports.

---

## 3. Hands-On Step-by-Step Walkthrough

### Step 1: Run the 12 Failure Scenarios Demo
```bash
# Execute 12 simulated failure scenarios (e.g. schema drift, lock contention, watermark drift)
PYTHONPATH=src python3 run_demo.py
```

### Step 2: Run Unit Tests
```bash
./venv/bin/pytest -v tests/unit/
```

### Step 3: Run Integration Tests
```bash
./venv/bin/pytest -v tests/integration/
```
