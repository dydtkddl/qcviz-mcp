## Conversation Context

If `conversation_context.active_molecule` is present in the input payload,
it means the user has been discussing this molecule in prior turns.

When the user's query lacks an explicit molecule name but contains:
- modification language (swap, replace, change substituent, 치환기 바꾸면, etc.)
- comparison language (compare, vs, 비교, etc.)
- implicit reference (그럼, 그러면, if we, what about, etc.)

Then you MUST:
1. Set `is_follow_up: true`
2. Set `molecule_from_context` to the active molecule name
3. For modification queries: set `lane: "chat_only"` (the modification
   exploration will be handled downstream)
4. Do NOT generate random molecule candidates

Example:
- Active molecule: "methylethylamine"
- User: "치환기를 하나만 바꾸면?"
- Correct output: lane="chat_only", is_follow_up=true,
  molecule_from_context="methylethylamine"
