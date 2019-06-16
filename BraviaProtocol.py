
class BraviaProtocol:
    protocol = { 'Power': 'PW'
                ,'Mute':  'MU'
                ,'Video': 'SV'
                ,'Volume': 'MV'
    }
    state = {}

    # def __init__():

    def makeQuery(self, parameters):
        queries = [];

        while parameters:
            if parameters[0] in self.protocol.keys():
                queries.append(self.protocol[parameters[0]] + "?")
            parameters = parameters[1:]

        return queries

    def makeCommands(self, params):
        commands = []

        for c, p in params.items():
            if c in self.protocol.keys():
                commands.append(str(list(self.protocol.values())[list(self.protocol.keys()).index(c)] + p))

        return commands



    def parseEvents(self, events):
        has_changed = False

        while events:
            ev = events[0][0:2]
            if ev in self.protocol.values():
                val = ''
                ob = events[0][2:]
                key = list(self.protocol.keys())[list(self.protocol.values()).index(ev)]

                if key in self.state.keys():
                    val = self.state[key]

                if ob != val:
                    has_changed = True
                    self.state[key] = ob

            events = events[1:]

        return has_changed


    def getState(self):
        return self.state
