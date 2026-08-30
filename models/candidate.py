class Candidate:
    def __init__(self, candidate_id, name):
        self.id = candidate_id
        self.name = name

    def __repr__(self):
        return "Candidate(%s, %s)" % (self.id, self.name)
