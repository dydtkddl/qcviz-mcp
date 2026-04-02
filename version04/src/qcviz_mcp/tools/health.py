import sys
import importlib
import importlib.util
from datetime import datetime, timezone
from qcviz_mcp.mcp_server import mcp
from qcviz_mcp.observability import metrics

@mcp.tool()
async def health_check() -> dict:
    """서버 상태 및 백엔드 가용성 진단."""
    
    backends = {}
    for name, module in [
        ("pyscf", "pyscf"),
        ("cclib", "cclib"),
        ("py3Dmol", "py3Dmol"),
        ("ase", "ase"),
        ("pyvista", "pyvista"),
        ("playwright", "playwright"),
    ]:
        try:
            mod = importlib.import_module(module)
            version = getattr(mod, "__version__", "unknown")
            backends[name] = {"available": True, "version": version}
        except ImportError:
            backends[name] = {"available": False}
    
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "python_version": sys.version,
        "qcviz_version": "0.6.0-alpha",
        "backends": backends,
        "metrics_summary": metrics.get_summary(),
        "renderer": _detect_renderer(),
    }

def _detect_renderer() -> str:
    if importlib.util.find_spec("pyvista") is not None:
        return "pyvista"
    if importlib.util.find_spec("playwright") is not None:
        return "playwright"
    return "py3dmol"
