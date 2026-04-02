# ═══════════════════════════════════════════════════════════════
# Prompt Asset Additions — 각 파일 맨 끝에 복사-붙여넣기
# ═══════════════════════════════════════════════════════════════


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FILE: src/qcviz_mcp/llm/prompt_assets/ingress_rewrite.md
# 파일 맨 끝에 추가:
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Korean Implicit Follow-up Patterns

- "치환기를 바꾸면?" → follow-up, modification_request
- "그럼 에너지는?" → follow-up, structure_reference
- "비교하면 어때?" → follow-up, comparison_request
- "하나만 바꿔보면?" → follow-up, modification_request

These patterns indicate the user is referencing the previously discussed
molecule. Do NOT strip these as noise. Mark is_follow_up=true.


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FILE: src/qcviz_mcp/llm/prompt_assets/grounding_decider.md
# 파일 맨 끝에 추가:
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Follow-up Context Rule

If the input is identified as an implicit follow-up (modification,
comparison, or structure reference), do NOT attempt to ground a new
molecule. Instead, set decision="direct_answer" and let the downstream
handler use the active_molecule from conversation state.


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# FILE: src/qcviz_mcp/llm/prompt_assets/semantic_expansion.md
# 파일 맨 끝에 추가:
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

## Modification Queries

For modification intent queries (substituent swap, R-group change),
do NOT expand into unrelated molecule names.
Instead, the grounding_queries should reference the scaffold molecule
from conversation context, e.g., "methylethylamine substituent
variations".
