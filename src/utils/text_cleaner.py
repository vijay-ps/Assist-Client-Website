import re

def clean_llm_output(text: str) -> str:
    if not text:
        return ""

    text = re.sub(r'^[\s*\-•]+', '', text, flags=re.MULTILINE)
    text = text.replace("*", "")
    text = re.sub(r'^#+\s*', '', text, flags=re.MULTILINE)
    text = re.sub(r'\n{2,}', '\n', text)

    return text.strip()
