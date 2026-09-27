import os
import yaml
from typing import Any, Dict
from src.common.exceptions import ConfigurationError

def load_yaml_config(path: str) -> Dict[str, Any]:
    """Loads and validates a YAML configuration file."""
    if not os.path.exists(path):
        raise ConfigurationError(f"Configuration file not found at path: {path}")
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            return data or {}
    except Exception as e:
        raise ConfigurationError(f"Failed to parse YAML file at {path}: {str(e)}")

class ConfigManager:
    """Manages system configuration across environments."""

    def __init__(self, config_dir: str = "config"):
        self.config_dir = config_dir
        self.env = os.getenv("APP_ENV", "local")
        self.environments = load_yaml_config(os.path.join(config_dir, "environments.yaml"))
        self.pipelines = load_yaml_config(os.path.join(config_dir, "pipelines.yaml"))
        self.healing_rules = load_yaml_config(os.path.join(config_dir, "healing_rules.yaml"))
        self.risk_policy = load_yaml_config(os.path.join(config_dir, "risk_policy.yaml"))
        self.data_quality = load_yaml_config(os.path.join(config_dir, "data_quality_rules.yaml"))
        self.lineage_sources = load_yaml_config(os.path.join(config_dir, "lineage_sources.yaml"))

    def get_env_config(self) -> Dict[str, Any]:
        return self.environments.get("environments", {}).get(self.env, {})

    def get_pipeline_config(self, pipeline_id: str) -> Dict[str, Any]:
        for pipe in self.pipelines.get("pipelines", []):
            if pipe.get("id") == pipeline_id:
                return pipe
        raise ConfigurationError(f"Pipeline ID '{pipeline_id}' not found in configuration.")
