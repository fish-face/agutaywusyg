### A location describes somewhere an object can be, and move to or from

class Location:
    def __init__(self, identifier, description=''):
        self.identifier = identifier
        self.description = description
        self.objects = []

    def describe(self):
        return self.description

    def __str__(self):
        return self.identifier

class Room(Location):
    def __init__(self, identifier, description='', exits=[]):
        self.exits = exits
        Location.__init__(self, identifier, description)

    def describe(self):
        r = self.description
        if self.exits:
            r += '\nExits are: ' + ', '.join(exits)
        else:
            r += '\nThere are no exits.'

        return r
