from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from qcviz_mcp.env_bootstrap import bootstrap_runtime_env

bootstrap_runtime_env()

# ── Phase 4: Phase 2~3 configuration constants ───────────────
# These provide a single source of truth. routing_config.py
# should import from here instead of duplicating.

# Phase 2: Modification
MODIFICATION_CONFIDENCE_THRESHOLD: float = float(
    os.environ.get("QCVIZ_MODIFICATION_CONFIDENCE_THRESHOLD", "0.60")
)
MODIFICATION_MAX_CANDIDATES: int = int(
    os.environ.get("QCVIZ_MODIFICATION_MAX_CANDIDATES", "5")
)

# Phase 3: Comparison
COMPARISON_MAX_CONCURRENT: int = int(
    os.environ.get("QCVIZ_COMPARISON_MAX_CONCURRENT", "3")
)
COMPARISON_TIMEOUT_SEC: float = float(
    os.environ.get("QCVIZ_COMPARISON_TIMEOUT_SEC", "300.0")
)


@dataclass(frozen=True)
class ServerConfig:
    """Server configuration loaded from the current process environment."""

    host: str = "127.0.0.1"
    port: int = 8765
    transport: str = "sse"

    max_atoms: int = 50
    max_workers: int = 2
    computation_timeout_seconds: float = 300.0
    default_basis: str = "sto-3g"
    default_cube_resolution: int = 80

    cache_max_size: int = 50
    cache_ttl_seconds: float = 3600.0

    rate_limit_capacity: int = 100
    rate_limit_refill_rate: float = 1.0
    allowed_output_root: Path = field(default_factory=lambda: Path.cwd() / "output")

    log_level: str = "INFO"
    log_json: bool = False
    preferred_renderer: str = "auto"

    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"
    gemini_timeout: float = 10.0
    gemini_temperature: float = 0.1

    molchat_base_url: str = "http://psid.aizen.co.kr/molchat"
    molchat_timeout: float = 15.0

    pubchem_timeout: float = 10.0
    pubchem_fallback: bool = True

    scf_cache_max_size: int = 256
    ion_offset_angstrom: float = 5.0
    context_tracking_enabled: bool = False

    @classmethod
    def from_env(cls) -> "ServerConfig":
        bootstrap_runtime_env()
        kwargs = {}
        alt_env_keys = {
            "gemini_api_key": "GEMINI_API_KEY",
            "gemini_model": "GEMINI_MODEL",
            "gemini_timeout": "GEMINI_TIMEOUT",
            "gemini_temperature": "GEMINI_TEMPERATURE",
            "molchat_base_url": "MOLCHAT_BASE_URL",
            "molchat_timeout": "MOLCHAT_TIMEOUT",
            "pubchem_timeout": "PUBCHEM_TIMEOUT",
            "scf_cache_max_size": "SCF_CACHE_MAX_SIZE",
            "ion_offset_angstrom": "ION_OFFSET_ANGSTROM",
            "context_tracking_enabled": "QCVIZ_CONTEXT_TRACKING_ENABLED",
        }

        for field_name, field_def in cls.__dataclass_fields__.items():
            env_key = f"QCVIZ_{field_name.upper()}"
            env_val = os.environ.get(env_key)
            if env_val is None and field_name in alt_env_keys:
                env_val = os.environ.get(alt_env_keys[field_name])
            if env_val is None:
                continue

            field_type = field_def.type
            if field_type in ("int", int):
                kwargs[field_name] = int(env_val)
            elif field_type in ("float", float):
                kwargs[field_name] = float(env_val)
            elif field_type in ("bool", bool):
                kwargs[field_name] = str(env_val).lower() in ("true", "1", "yes")
            elif "Path" in str(field_type):
                kwargs[field_name] = Path(env_val)
            else:
                kwargs[field_name] = env_val

        return cls(**kwargs)
