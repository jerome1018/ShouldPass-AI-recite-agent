import os
import yaml

_PROJECT_ROOT = None


def get_project_root():
    global _PROJECT_ROOT
    if _PROJECT_ROOT is None:
        _PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return _PROJECT_ROOT


def load_config():
    config_path = os.path.join(get_project_root(), "config.yaml")
    if not os.path.exists(config_path):
        raise FileNotFoundError(
            f"config.yaml not found at {config_path}\n"
            "Copy config.yaml.example or create one with your LLM API settings."
        )
    with open(config_path, "r") as f:
        return yaml.safe_load(f)
