# 20 Presenter Demonstration Script

## Step-by-Step Demonstration Walkthrough

1. **Environment Setup**:
   ```bash
   bash scripts/bootstrap.sh
   ```

2. **Execute Full Demo**:
   ```bash
   python3 run_demo.py --all-scenarios
   ```

3. **Query BFS Upstream Lineage**:
   ```bash
   python3 run_demo.py --lineage-upstream fact_orders
   ```

4. **Query BFS Downstream Lineage & Blast Radius**:
   ```bash
   python3 run_demo.py --lineage-downstream source_orders
   ```

5. **Run Test Suite**:
   ```bash
   bash scripts/run_tests.sh
   ```
