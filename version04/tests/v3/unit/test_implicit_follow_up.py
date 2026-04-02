from __future__ import annotations

import pytest

from qcviz_mcp.llm.normalizer import detect_implicit_follow_up
from qcviz_mcp.llm.schemas import IngressResult


def test_ingress_result_has_context_molecule_fields() -> None:
    result = IngressResult()

    assert hasattr(result, "context_molecule_name")
    assert hasattr(result, "context_molecule_smiles")
    assert result.context_molecule_name is None
    assert result.context_molecule_smiles is None


@pytest.mark.parametrize(
    ("message", "expected_type"),
    [
        ("치환기를 하나만 바꾸면?", "modification_request"),
        ("메틸기를 에틸기로 교체하면 어떻게 돼?", "modification_request"),
        ("작용기를 제거하면?", "modification_request"),
        ("what if I swap the methyl group?", "modification_request"),
        ("if we replace the substituent with ethyl", "modification_request"),
        ("이성질체랑 비교하면?", "comparison_request"),
        ("compare with the isomer", "comparison_request"),
        ("차이가 뭐야?", "comparison_request"),
        ("그럼 에너지는?", "structure_reference"),
        ("그럼 HOMO는 어떻게 생겼어?", "structure_reference"),
        ("만약 온도를 올리면?", "structure_reference"),
    ],
)
def test_detect_implicit_follow_up_positive_cases(message: str, expected_type: str) -> None:
    result = detect_implicit_follow_up(
        message,
        has_active_molecule=True,
        has_explicit_molecule_name=False,
    )

    assert result["is_implicit_follow_up"] is True
    assert result["follow_up_type"] == expected_type


def test_detect_implicit_follow_up_requires_active_molecule() -> None:
    result = detect_implicit_follow_up(
        "치환기를 하나만 바꾸면?",
        has_active_molecule=False,
        has_explicit_molecule_name=False,
    )

    assert result["is_implicit_follow_up"] is False
    assert result["modification_detected"] is True


def test_detect_implicit_follow_up_requires_omitted_molecule_name() -> None:
    result = detect_implicit_follow_up(
        "벤젠의 치환기를 바꾸면?",
        has_active_molecule=True,
        has_explicit_molecule_name=True,
    )

    assert result["is_implicit_follow_up"] is False


@pytest.mark.parametrize("message", ["양자화학이 뭐야?", "안녕하세요", "", None])
def test_detect_implicit_follow_up_ignores_non_follow_ups(message: str | None) -> None:
    result = detect_implicit_follow_up(
        message,
        has_active_molecule=True,
        has_explicit_molecule_name=False,
    )

    assert result["is_implicit_follow_up"] is False
