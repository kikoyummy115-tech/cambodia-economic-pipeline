def hhi_from_shares(shares: list[float]) -> float:
    """Return the Herfindahl-Hirschman Index on a 0–1 scale.

    Shares must be proportions (for example 0.60, not 60).
    The input should represent mutually exclusive categories whose shares
    sum to approximately 1.
    """
    if not shares:
        raise ValueError("At least one share is required")
    if any(s < 0 or s > 1 for s in shares):
        raise ValueError("Each share must be between 0 and 1")
    if abs(sum(shares) - 1.0) > 0.02:
        raise ValueError("Shares must sum to approximately 1.0")
    return sum(s * s for s in shares)
