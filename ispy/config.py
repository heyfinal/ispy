"""
iSpy Configuration Management
"""

import os
import json
from pathlib import Path
from typing import Optional, Any, Dict
from dataclasses import dataclass, field

# Optional imports
try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False
    load_dotenv = lambda: None  # No-op

from .constants import DEFAULT_CONFIG_DIR, AI_DEFAULT_MODEL, DEFAULT_BACKUP_ROOT


@dataclass
class Config:
    """iSpy Configuration"""

    # AI Settings
    openai_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    ai_model: str = AI_DEFAULT_MODEL
    gemini_model: str = "gemini-1.5-flash"
    ai_enabled: bool = True
    openai_base_url: Optional[str] = None

    # Output Settings
    output_dir: Path = field(default_factory=lambda: Path.home() / "ispy_reports")
    log_level: str = "INFO"
    color_output: bool = True

    # Module Settings
    enabled_modules: list = field(default_factory=lambda: [
        "battery", "storage", "network", "apps", "security",
        "performance", "thermal", "backup", "accessibility", "crashes"
    ])

    # Device Settings
    auto_select_device: bool = True
    default_device_udid: Optional[str] = None

    # Backup Settings
    backup_root: Path = field(default_factory=lambda: Path(DEFAULT_BACKUP_ROOT).expanduser())
    case_output_dir: Path = field(default_factory=lambda: Path.home() / "ispy_cases")

    # Report Settings
    report_format: str = "markdown"  # markdown, json, html, pdf
    include_recommendations: bool = True
    include_ai_analysis: bool = True

    _config_path: Path = field(default_factory=lambda: Path.home() / ".ispy" / "config.yaml")

    def __post_init__(self):
        """Load environment variables and config file"""
        load_dotenv()

        # Load from environment
        if not self.openai_api_key:
            self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.gemini_api_key:
            self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        if not self.openai_base_url:
            self.openai_base_url = os.getenv("ISPY_OPENAI_BASE_URL") or os.getenv("OPENAI_BASE_URL")

        if os.getenv("ISPY_AI_MODEL"):
            self.ai_model = os.getenv("ISPY_AI_MODEL")
        if os.getenv("ISPY_GEMINI_MODEL"):
            self.gemini_model = os.getenv("ISPY_GEMINI_MODEL")

        # Create config directory if needed
        self._config_path.parent.mkdir(parents=True, exist_ok=True)

        # Load from config file if exists
        if self._config_path.exists():
            self._load_from_file()

    def _load_from_file(self):
        """Load configuration from YAML or JSON file"""
        try:
            with open(self._config_path, 'r') as f:
                content = f.read()

            # Try YAML first if available, then JSON
            if YAML_AVAILABLE:
                data = yaml.safe_load(content) or {}
            else:
                data = json.loads(content) if content.strip() else {}

            # AI settings
            ai_config = data.get("ai", {})
            if ai_config.get("model"):
                self.ai_model = ai_config["model"]
            if ai_config.get("gemini_model"):
                self.gemini_model = ai_config["gemini_model"]
            if ai_config.get("api_key"):
                self.openai_api_key = ai_config["api_key"]
            if ai_config.get("gemini_api_key"):
                self.gemini_api_key = ai_config["gemini_api_key"]
            if ai_config.get("openai_base_url"):
                self.openai_base_url = ai_config["openai_base_url"]
            if ai_config.get("enabled") is not None:
                self.ai_enabled = ai_config["enabled"]

            # Output settings
            output_config = data.get("output", {})
            if output_config.get("dir"):
                self.output_dir = Path(output_config["dir"]).expanduser()
            if output_config.get("log_level"):
                self.log_level = output_config["log_level"]
            if output_config.get("color") is not None:
                self.color_output = output_config["color"]

            # Backup settings
            backup_config = data.get("backup", {})
            if backup_config.get("root"):
                self.backup_root = Path(backup_config["root"]).expanduser()
            if backup_config.get("case_output_dir"):
                self.case_output_dir = Path(backup_config["case_output_dir"]).expanduser()

            # Module settings
            if data.get("modules"):
                self.enabled_modules = data["modules"]

            # Device settings
            device_config = data.get("device", {})
            if device_config.get("auto_select") is not None:
                self.auto_select_device = device_config["auto_select"]
            if device_config.get("default_udid"):
                self.default_device_udid = device_config["default_udid"]

            # Report settings
            report_config = data.get("report", {})
            if report_config.get("format"):
                self.report_format = report_config["format"]
            if report_config.get("include_recommendations") is not None:
                self.include_recommendations = report_config["include_recommendations"]
            if report_config.get("include_ai_analysis") is not None:
                self.include_ai_analysis = report_config["include_ai_analysis"]

        except Exception as e:
            print(f"Warning: Could not load config file: {e}")

    def save(self):
        """Save configuration to YAML file"""
        data = {
            "ai": {
                "api_key": self.openai_api_key,
                "gemini_api_key": self.gemini_api_key,
                "model": self.ai_model,
                "gemini_model": self.gemini_model,
                "enabled": self.ai_enabled,
                "openai_base_url": self.openai_base_url,
            },
            "output": {
                "dir": str(self.output_dir),
                "log_level": self.log_level,
                "color": self.color_output,
            },
            "modules": self.enabled_modules,
            "device": {
                "auto_select": self.auto_select_device,
                "default_udid": self.default_device_udid,
            },
            "report": {
                "format": self.report_format,
                "include_recommendations": self.include_recommendations,
                "include_ai_analysis": self.include_ai_analysis,
            },
            "backup": {
                "root": str(self.backup_root),
                "case_output_dir": str(self.case_output_dir),
            },
        }

        with open(self._config_path, 'w') as f:
            if YAML_AVAILABLE:
                yaml.dump(data, f, default_flow_style=False)
            else:
                json.dump(data, f, indent=2)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "ai_model": self.ai_model,
            "gemini_model": self.gemini_model,
            "ai_enabled": self.ai_enabled,
            "output_dir": str(self.output_dir),
            "log_level": self.log_level,
            "enabled_modules": self.enabled_modules,
            "report_format": self.report_format,
            "openai_api_key": self.openai_api_key,
            "gemini_api_key": self.gemini_api_key,
            "openai_base_url": self.openai_base_url,
            "backup_root": str(self.backup_root),
            "case_output_dir": str(self.case_output_dir),
        }

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key"""
        return getattr(self, key, default)

    @classmethod
    def get_default_config_path(cls) -> Path:
        """Get default config file path"""
        return Path.home() / ".ispy" / "config.yaml"

    @classmethod
    def create_default_config(cls) -> "Config":
        """Create and save default configuration"""
        config = cls()
        config.save()
        return config
