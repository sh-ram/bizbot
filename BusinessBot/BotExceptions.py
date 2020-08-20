class JobException(Exception):
    def __init__(self, name):
        self.text = f'JobExeption: {name}'

class RePatternException(Exception):
    def __init__(self, name):
        self.text = f'RePatternExeption: {name}'

class CurrencyException(Exception):
    def __init__(self, name):
        self.text = f'RePatternExeption: {name}'

class WebException(Exception):
    def __init__(self, name):
        self.text = f'WebException: {name}'