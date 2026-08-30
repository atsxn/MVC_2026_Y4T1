class Voter:
    def __init__(self, voter_id, name, active=True):
        self.id = voter_id
        self.name = name
        self.active = active
        self.has_voted = False

    def __repr__(self):
        return "Voter(%s, voted=%s)" % (self.id, self.has_voted)
