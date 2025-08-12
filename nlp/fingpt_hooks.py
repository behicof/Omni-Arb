"""Hooks to interact with FinGPT models (mocked)."""

def summarize(text: str) -> str:
    """Return a dummy summary for given text."""
    return f"summary: {text[:50]}"


def explain_trade(trade: str) -> str:
    """Explain trade outcome in natural language."""
    return f"Trade explanation: {trade}"
