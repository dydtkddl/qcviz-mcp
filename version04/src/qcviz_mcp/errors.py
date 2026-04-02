from __future__ import annotations

from enum import Enum
from typing import Any


class ErrorCategory(str, Enum):
    VALIDATION = "validation"
    CONVERGENCE = "convergence"
    RESOURCE = "resource"
    BACKEND = "backend"
    INTERNAL = "internal"


class QCVizError(Exception):
    """Base error for QCViz application failures."""

    def __init__(
        self,
        message: str,
        category: ErrorCategory,
        suggestion: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.category = category
        self.suggestion = suggestion
        self.details = details or {}

    def to_mcp_response(self) -> dict[str, Any]:
        """Render a normalized MCP error payload."""
        resp: dict[str, Any] = {
            "error": {
                "category": self.category.value,
                "message": str(self),
            }
        }
        if self.suggestion:
            resp["error"]["suggestion"] = self.suggestion
        return resp


class ValidationError(QCVizError):
    def __init__(self, message: str, **kwargs: Any) -> None:
        super().__init__(message, ErrorCategory.VALIDATION, **kwargs)


class ConvergenceError(QCVizError):
    def __init__(
        self,
        message: str,
        strategies_tried: list[str] | None = None,
        **kwargs: Any,
    ) -> None:
        suggestion = (
            "Try: (1) a smaller basis set, (2) adaptive=True for 5-level escalation, "
            "(3) providing an initial guess, or (4) checking molecular geometry."
        )
        super().__init__(message, ErrorCategory.CONVERGENCE, suggestion=suggestion, **kwargs)
        self.strategies_tried = strategies_tried or []


class ResourceError(QCVizError):
    def __init__(self, message: str, **kwargs: Any) -> None:
        super().__init__(message, ErrorCategory.RESOURCE, **kwargs)


class BackendError(QCVizError):
    def __init__(self, message: str, backend_name: str = "", **kwargs: Any) -> None:
        super().__init__(message, ErrorCategory.BACKEND, **kwargs)
        self.backend_name = backend_name


class ModificationError(QCVizError):
    """Phase 2: Error during molecular structure modification.

    Raised when substituent identification, swapping, or candidate
    generation fails.
    """

    def __init__(
        self,
        message: str,
        *,
        base_smiles: str | None = None,
        from_group: str | None = None,
        to_group: str | None = None,
        suggestion: str = (
            "Check that the base molecule contains the specified substituent."
        ),
        details: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> None:
        merged_details = dict(details or {})
        merged_details.update(
            {
                k: v
                for k, v in {
                    "base_smiles": base_smiles,
                    "from_group": from_group,
                    "to_group": to_group,
                }.items()
                if v is not None
            }
        )
        merged_details.update({k: v for k, v in kwargs.items() if v is not None})
        super().__init__(
            message,
            ErrorCategory.VALIDATION,
            suggestion=suggestion,
            details=merged_details,
        )


class StructureIntelligenceError(QCVizError):
    """Phase 2: Internal error in the structure intelligence service."""

    def __init__(
        self,
        message: str,
        *,
        details: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> None:
        merged_details = dict(details or {})
        merged_details.update({k: v for k, v in kwargs.items() if v is not None})
        super().__init__(
            message,
            ErrorCategory.BACKEND,
            details=merged_details,
        )


class ComparisonError(QCVizError):
    """Phase 3: Error during molecular comparison workflow."""

    def __init__(
        self,
        message: str,
        *,
        mol_a: str | None = None,
        mol_b: str | None = None,
        suggestion: str = (
            "Ensure both molecules resolve correctly before comparing."
        ),
        details: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> None:
        merged_details = dict(details or {})
        merged_details.update(
            {
                k: v
                for k, v in {"mol_a": mol_a, "mol_b": mol_b}.items()
                if v is not None
            }
        )
        merged_details.update({k: v for k, v in kwargs.items() if v is not None})
        super().__init__(
            message,
            ErrorCategory.VALIDATION,
            suggestion=suggestion,
            details=merged_details,
        )


class ComparisonTimeoutError(ComparisonError):
    """Phase 3: Comparison job exceeded the allowed time limit."""

    def __init__(
        self,
        message: str = "Comparison job timed out",
        **kwargs: Any,
    ) -> None:
        super().__init__(
            message,
            suggestion="Try simpler molecules or a smaller basis set.",
            **kwargs,
        )
