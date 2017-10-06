from abc import ABCMeta, abstractmethod


class AbstractAutomata:
    __metaclass__ = ABCMeta

    def __init__(self):
        self.states = []

    def consume_stream(self, char_stream):
        for char in char_stream:
            self.consume(char)

    @abstractmethod
    def consume(self, char):
        pass

    @abstractmethod
    @property
    def current_state(self):
        pass


class State:
    def __init__(self):
        self.transitions = dict()
        self.reached_call = lambda: None

    @classmethod
    def end_state(cls, reached_call):
        result = cls()
        result.reached_call = reached_call
        return result

    def __getitem__(self, item):
        return self.transitions[item]


class Automata(AbstractAutomata):
    def __init__(self):
        AbstractAutomata.__init__(self)
        self.state_index = 0

    def consume(self, char):
        self.state_index = self.current_state[char]
        new_state = self.current_state
        new_state.reached_call()

    @property
    def current_state(self):
        return self.states[self.state_index]


class NDAutomata(AbstractAutomata):
    def __init__(self):
        AbstractAutomata.__init__(self)
        self.state_indices = {0}

    @property
    def current_state(self):
        return (self.states[state_index] for state_index in self.state_indices)

    def consume(self, char):
        new_states_indices = []
        for state in self.current_state:
            new_states_indices.extend(state[char])
        self.state_indices = set(new_states_indices)
        new_states = self.current_state
        for state in new_states:
            state.reached_call()
