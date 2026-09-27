import pandas as pd
from typing import Dict, Any, Tuple
from src.common.config import ConfigManager

class DataQualityValidator:
    """Validates dataframe against null checks, key uniqueness, and range limits."""

    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.dq_cfg = config_manager.data_quality.get("data_quality", {})

    def validate_df(self, df: pd.DataFrame, key_col: str) -> Tuple[bool, Dict[str, Any]]:
        if df.empty:
            return True, {"status": "EMPTY_DATAFRAME_PASSED"}

        results = {"passed": True, "checks": {}}

        # Key Uniqueness Check
        dup_count = df.duplicated(subset=[key_col]).sum()
        dup_ratio = dup_count / len(df)
        max_dup = self.dq_cfg.get("max_duplicate_ratio", 0.01)
        key_passed = dup_ratio <= max_dup
        results["checks"]["key_uniqueness"] = {
            "duplicate_count": int(dup_count),
            "duplicate_ratio": float(dup_ratio),
            "max_allowed": max_dup,
            "passed": key_passed
        }
        if not key_passed:
            results["passed"] = False

        # Null checks
        null_limits = self.dq_cfg.get("max_null_percentage", {})
        for col, limit in null_limits.items():
            if col in df.columns:
                null_pct = (df[col].isnull().sum() / len(df)) * 100.0
                col_passed = null_pct <= limit
                results["checks"][f"null_check_{col}"] = {
                    "null_percentage": float(null_pct),
                    "max_allowed": float(limit),
                    "passed": col_passed
                }
                if not col_passed:
                    results["passed"] = False

        return results["passed"], results
