class Result:
    """What a controller hands back to the view: did it work, what to say amd what to show."""

    def __init__(self, ok, message="", data=None):
        self.ok = ok
        self.message = message
        self.data = data

    @classmethod
    # pass
    def success(cls, message="", data=None):
        return cls(True, message, data)

    @classmethod
    # fail
    def failure(cls, message):
        return cls(False, message)
