import re
from typing import Dict, List, Any, Optional
from src.common.models import FailureEvent, ClassificationResult
from src.common.config import ConfigManager
from src.common.logging import get_logger

logger = get_logger("signature_classifier")

class SignatureClassifier:
    """Classifies FailureEvents using deterministic ordered rules in healing_rules.yaml."""

    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.rules = config_manager.healing_rules.get("rules", [])
        # Sort rules by priority ascending (lower number = higher priority)
        self.rules = sorted(self.rules, key=lambda r: r.get("priority", 100))

    def classify(self, event: FailureEvent) -> ClassificationResult:
        matched_results = []

        for rule in self.rules:
            rule_id = rule["id"]
            rule_version = rule.get("version", 1)
            match_cfg = rule.get("match", {})
            err_codes = match_cfg.get("error_codes", [])
            msg_regex = match_cfg.get("message_regex", "")

            code_match = event.error_code in err_codes
            msg_match = bool(re.search(msg_regex, event.error_message, re.IGNORECASE)) if msg_regex else False

            if code_match or msg_match:
                matched_conditions = []
                if code_match:
                    matched_conditions.append(f"error_code '{event.error_code}' in {err_codes}")
                if msg_match:
                    matched_conditions.append(f"error_message matched regex '{msg_regex}'")

                matched_results.append(ClassificationResult(
                    rule_id=rule_id,
                    rule_version=rule_version,
                    classification=rule["classification"],
                    runbook_id=rule.get("runbook_id"),
                    confidence=1.0 if (code_match and msg_match) else 0.85,
                    matched_conditions=matched_conditions,
                    evidence_references=[f"event_id:{event.event_id}"]
                ))

        if not matched_results:
            logger.warning(f"No rule matched event {event.event_id}. Defaulting to MANUAL_REVIEW_REQUIRED.")
            return ClassificationResult(
                rule_id="RULE-DEFAULT-000",
                rule_version=1,
                classification="MANUAL_REVIEW_REQUIRED",
                runbook_id="RB-ESCALATE-001",
                confidence=0.0,
                matched_conditions=["No rule matched failure signature"],
                evidence_references=[f"event_id:{event.event_id}"]
            )

        if len(matched_results) > 1 and matched_results[0].confidence == matched_results[1].confidence and matched_results[0].classification != matched_results[1].classification:
            logger.warning(f"Conflicting matching rules for event {event.event_id}. Escalating.")
            return ClassificationResult(
                rule_id="RULE-CONFLICT-000",
                rule_version=1,
                classification="MANUAL_REVIEW_REQUIRED",
                runbook_id="RB-ESCALATE-001",
                confidence=0.5,
                matched_conditions=["Conflicting rules matched failure signature"],
                evidence_references=[f"event_id:{event.event_id}"]
            )

        logger.info(f"Classified event {event.event_id} as '{matched_results[0].classification}' using rule {matched_results[0].rule_id}")
        return matched_results[0]
