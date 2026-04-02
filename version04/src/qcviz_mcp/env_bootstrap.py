from __future__ import annotations

import ast
import logging
import os
import re
import threading
from pathlib import Path
from typing import Any, Dict, Optional

_ENV_LINE_RE = re.compile(r"^\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)\s*$")
_BOOTSTRAP_LOCK = threading.Lock()
_BOOTSTRAP_STATUS: Dict[str, Any] = {
    "attempted": False,
    "loaded": False,
    "path": "",
    "file_exists": False,
    "loader": None,
    "keys_loaded": 0,
    "error": None,
}
logger = logging.getLogger(__name__)

# ── Phase 4: Feature flag registry ───────────────────────────
_FEATURE_FLAGS: Dict[str, tuple[str, str]] = {
    "QCVIZ_CONTEXT_TRACKING_ENABLED": (
        "false", "Phase 1 conversation context tracking",
    ),
    "QCVIZ_MODIFICATION_LANE_ENABLED": (
        "false", "Phase 2 modification exploration lane",
    ),
    "QCVIZ_COMPARISON_ENABLED": (
        "false", "Phase 3 comparison & delta view",
    ),
}


def _resolve_dotenv_path(dotenv_path: Optional[os.PathLike[str] | str] = None) -> Path:
    if dotenv_path is not None:
        return Path(dotenv_path).expanduser().resolve()
    return Path(__file__).resolve().parents[2] / ".env"


def _parse_env_value(raw_value: str) -> str:
    value = str(raw_value or "").strip()
    if not value:
        return ""
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        try:
            parsed = ast.literal_eval(value)
            return str(parsed)
        except Exception:
            return value[1:-1]
    value = re.sub(r"\s+#.*$", "", value).strip()
    return value


def _load_with_python_dotenv(path: Path, *, override: bool) -> Optional[int]:
    try:
        from dotenv import load_dotenv
    except ImportError:
        return None
    load_dotenv(path, override=override)
    return 0


def _load_with_manual_parser(path: Path, *, override: bool) -> int:
    loaded = 0
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        match = _ENV_LINE_RE.match(line)
        if not match:
            continue
        key, raw_value = match.groups()
        if not override and key in os.environ:
            continue
        os.environ[key] = _parse_env_value(raw_value)
        loaded += 1
    return loaded


def _log_feature_flags() -> Dict[str, bool]:
    """Check and log the status of all Phase 1~3 feature flags."""
    flags: Dict[str, bool] = {}
    for key, (default, desc) in _FEATURE_FLAGS.items():
        raw = os.environ.get(key, default).strip().lower()
        enabled = raw in ("1", "true", "yes", "on")
        flags[key] = enabled
        logger.info(
            "Feature flag %s (%s): %s",
            key, desc, "ENABLED" if enabled else "disabled",
        )
    return flags


def get_feature_flags() -> Dict[str, bool]:
    """Return current feature flag states for external modules."""
    return _log_feature_flags()


def bootstrap_runtime_env(
    *,
    dotenv_path: Optional[os.PathLike[str] | str] = None,
    override: bool = False,
    force: bool = False,
) -> bool:
    path = _resolve_dotenv_path(dotenv_path)
    cached_path = str(path)
    with _BOOTSTRAP_LOCK:
        if (
            not force
            and _BOOTSTRAP_STATUS.get("attempted")
            and _BOOTSTRAP_STATUS.get("path") == cached_path
        ):
            return bool(_BOOTSTRAP_STATUS.get("loaded"))

    status: Dict[str, Any] = {
        "attempted": True,
        "loaded": False,
        "path": cached_path,
        "file_exists": path.exists(),
        "loader": None,
        "keys_loaded": 0,
        "error": None,
    }

    try:
        if path.exists():
            dotenv_loaded = _load_with_python_dotenv(path, override=override)
            if dotenv_loaded is None:
                status["loader"] = "manual"
                status["keys_loaded"] = _load_with_manual_parser(path, override=override)
            else:
                status["loader"] = "python-dotenv"
                status["keys_loaded"] = max(0, int(dotenv_loaded))
            status["loaded"] = True
        else:
            status["error"] = "dotenv_file_missing"
    except Exception as exc:
        status["error"] = f"{type(exc).__name__}: {exc}"

    status["feature_flags"] = _log_feature_flags()

    with _BOOTSTRAP_LOCK:
        _BOOTSTRAP_STATUS.update(status)
        return bool(_BOOTSTRAP_STATUS.get("loaded"))


def get_env_bootstrap_status() -> Dict[str, Any]:
    with _BOOTSTRAP_LOCK:
        return dict(_BOOTSTRAP_STATUS)


def _reset_env_bootstrap_state_for_tests() -> None:
    with _BOOTSTRAP_LOCK:
        _BOOTSTRAP_STATUS.clear()
        _BOOTSTRAP_STATUS.update(
            {
                "attempted": False,
                "loaded": False,
                "path": "",
                "file_exists": False,
                "loader": None,
                "keys_loaded": 0,
                "error": None,
                "feature_flags": {},
            }
        )
