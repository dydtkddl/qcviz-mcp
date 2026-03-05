"""
테스트 도중 발생할 수 있는 의존성 및 백엔드 설정 관련 테스트.
"""
import pytest
from qcviz_mcp.backends.registry import registry
from qcviz_mcp.backends.base import OrbitalBackend

def test_registry_has_backends():
    """레지스트리에 백엔드가 정상적으로 감지되는지 확인합니다."""
    
    try:
        # PySCF
        pytest.importorskip("pyscf")
        pyscf_backend = registry.get("pyscf")
        assert pyscf_backend is not None
        assert isinstance(pyscf_backend, OrbitalBackend)
        assert pyscf_backend.name() == "pyscf"
    except pytest.skip.Exception:
        pass

    try:
        # cclib
        pytest.importorskip("cclib")
        cclib_backend = registry.get("cclib")
        assert cclib_backend is not None
        assert cclib_backend.name() == "cclib"
    except pytest.skip.Exception:
        pass

    try:
        # py3Dmol
        pytest.importorskip("py3Dmol")
        viz_backend = registry.get("py3dmol")
        assert viz_backend is not None
        assert viz_backend.name() == "py3dmol"
    except pytest.skip.Exception:
        pass
    
    try:
        # ASE
        pytest.importorskip("ase")
        ase_backend = registry.get("ase")
        assert ase_backend is not None
        assert ase_backend.name() == "ase"
    except pytest.skip.Exception:
        pass

def test_unknown_backend():
    """알 수 없는 백엔드를 요청할 때의 예외 처리 확인."""
    with pytest.raises(ValueError, match="알 수 없는 백엔드: unknown"):
        registry.get("unknown")
