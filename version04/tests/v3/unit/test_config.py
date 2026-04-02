"""Unit tests for qcviz_mcp.config."""

from __future__ import annotations

import os
from unittest.mock import patch

from qcviz_mcp.config import ServerConfig


class TestServerConfigDefaults:
    def test_default_gemini_model(self) -> None:
        cfg = ServerConfig()
        assert cfg.gemini_model == "gemini-2.5-flash"

    def test_default_molchat_url(self) -> None:
        cfg = ServerConfig()
        assert "molchat" in cfg.molchat_base_url

    def test_default_pubchem_fallback(self) -> None:
        cfg = ServerConfig()
        assert cfg.pubchem_fallback is True

    def test_default_scf_cache_max_size(self) -> None:
        cfg = ServerConfig()
        assert cfg.scf_cache_max_size == 256

    def test_default_ion_offset(self) -> None:
        cfg = ServerConfig()
        assert cfg.ion_offset_angstrom == 5.0

    def test_default_gemini_timeout(self) -> None:
        cfg = ServerConfig()
        assert cfg.gemini_timeout == 10.0

    def test_default_preferred_renderer(self) -> None:
        cfg = ServerConfig()
        assert cfg.preferred_renderer == "auto"

    def test_default_context_tracking_disabled(self) -> None:
        cfg = ServerConfig()
        assert cfg.context_tracking_enabled is False


class TestServerConfigFromEnv:
    def test_from_env_loads_gemini_key(self) -> None:
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key-123"}, clear=False):
            cfg = ServerConfig.from_env()
            assert cfg.gemini_api_key == "test-key-123"

    def test_from_env_qcviz_prefix(self) -> None:
        with patch.dict(os.environ, {"QCVIZ_GEMINI_MODEL": "gemini-3.0"}, clear=False):
            cfg = ServerConfig.from_env()
            assert cfg.gemini_model == "gemini-3.0"

    def test_from_env_override_numeric(self) -> None:
        with patch.dict(os.environ, {"QCVIZ_SCF_CACHE_MAX_SIZE": "512"}, clear=False):
            cfg = ServerConfig.from_env()
            assert cfg.scf_cache_max_size == 512

    def test_from_env_alt_key(self) -> None:
        with patch.dict(os.environ, {"SCF_CACHE_MAX_SIZE": "1024"}, clear=False):
            cfg = ServerConfig.from_env()
            assert cfg.scf_cache_max_size in (256, 1024)

    def test_from_env_context_tracking_enabled(self) -> None:
        with patch.dict(os.environ, {"QCVIZ_CONTEXT_TRACKING_ENABLED": "true"}, clear=False):
            cfg = ServerConfig.from_env()
            assert cfg.context_tracking_enabled is True
