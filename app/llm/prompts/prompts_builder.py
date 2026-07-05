def build_prompt(
    role: str,
    objective: str,
    context: str,
    instructions: str,
) -> str:
    return f"""
You are a {role}.

OBJECTIVE:
{objective}

CONTEXT:
{context}

INSTRUCTIONS:
{instructions}
""".strip()