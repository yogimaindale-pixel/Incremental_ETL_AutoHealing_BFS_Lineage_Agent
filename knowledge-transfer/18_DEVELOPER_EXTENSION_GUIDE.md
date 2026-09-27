# 18 Developer Extension Guide

## 1. Adding a New Failure Signature Rule
1. Open `config/healing_rules.yaml`.
2. Add a new rule entry with `rule_id`, `error_code_pattern`, `error_message_pattern`, `classification`, `confidence`, and `runbook_id`.
3. Add corresponding unit test in `tests/unit/test_signature_classifier.py`.

## 2. Adding a New Runbook
1. Implement the runbook handler method in `src/healing/runbook_registry.py`.
2. Map rule in `config/healing_rules.yaml`.
3. Add unit test in `tests/unit/test_runbooks.py`.
