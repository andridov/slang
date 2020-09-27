
class SlProgramStatus(Exception):
    def __init__(self, expression, message):
        self.expression = expression
        self.message = message



class SlPluginEntryPointStatus(Exception):
    def __init__(self, expression, message):
        self.expression = expression
        self.message = message



# terminates plugin execution but continue executing other plugins
class SlPluginStatus(Exception):
    def __init__(self, expression, message):
        self.expression = expression
        self.message = message
