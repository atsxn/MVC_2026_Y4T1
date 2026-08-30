class RuleViolation(Exception):
    """An action was rejected by an election rule. The message is shown to the user as-is."""
    # custom exception used to separate business rule errors 
    # from standard system bugs like a TypeError or KeyError
    pass
