# Incremental ETL Auto-Healing BFS Lineage Agent

Welcome to the **Incremental ETL Auto-Healing BFS Lineage Agent Platform** (Simplified & Line-by-Line Commented Edition).

This repository implements an enterprise-grade, autonomous data engineering system capable of detecting incremental ETL failures, classifying signatures, running Breadth-First Search (BFS) graph lineage traversals, selecting auto-healing runbooks, executing remediation, validating post-healing data quality, and managing circuit breaker rollbacks.

---

## 🚀 Quick Start Instructions

### 1. Environment Setup
```bash
# Clone the repository over SSH
git clone git@github.com:yogimaindale-pixel/Incremental_ETL_AutoHealing_BFS_Lineage_Agent.git
cd Incremental_ETL_AutoHealing_BFS_Lineage_Agent

# Create and activate local Python virtual environment
python3 -m venv venv
source venv/bin/activate

# Install required packages
pip install -r requirements.txt
pip install httpx
```

### 2. Run Demo Walkthrough (12 Failure Scenarios)
Execute the complete end-to-end incident detection and auto-healing suite:
```bash
PYTHONPATH=src python3 run_demo.py
```

### 3. Run Automated Tests
```bash
./venv/bin/pytest -v
```

---

## 🏛️ Architecture & Incident State Machine

```
[ Failure Event ] ──► DETECTED ──► NORMALIZED ──► CLASSIFIED ──► EVIDENCE_COLLECTED
                                                                      │
[ RECOVERED / CLOSED ] ◄── VALIDATING ◄── REMEDIATING ◄── LINEAGE_TRAVERSED (BFS)
                                 │
                          [ ROLLED_BACK / ESCALATED ]
```

---

## 📚 Complete Documentation Catalog

* 📘 [DOCUMENTATION.md](file:///config/Desktop/Incremental_ETL_AutoHealing_BFS_Lineage_Agent/DOCUMENTATION.md): Deep-dive technical requirements, architecture design, database schemas, and signature classification rules.
* 🎓 [KNOWLEDGE_TRANSFER.md](file:///config/Desktop/Incremental_ETL_AutoHealing_BFS_Lineage_Agent/KNOWLEDGE_TRANSFER.md): Junior developer onboarding guide, concept explainers (BFS Lineage, State Machine, Auto-Healing Runbooks), and step-by-step hands-on tutorials.
