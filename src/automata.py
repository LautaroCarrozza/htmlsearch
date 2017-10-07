from abc import ABCMeta, abstractmethod

LAMBDA = ''
SPACE = ' '


class AbstractAutomata:
    __metaclass__ = ABCMeta

    def __init__(self, init_state):
        self.init_state = init_state

    def consume_stream(self, char_stream):
        for char in char_stream:
            self.consume(char)

    @abstractmethod
    def consume(self, char):
        pass

    @abstractmethod
    def current_state(self):
        pass

    '''
    def __str__(self):
        result_list = ['q{} => {}'.format(index, state) for index, state in enumerate(self.states)]
        return '\n'.join(result_list)

    def __repr__(self):
        return str(self)
    '''


class State:
    def __init__(self, default_state):
        self.transitions = dict()
        self.default_state = default_state
        self.reached_call = lambda: None

    @classmethod
    def end_state(cls, default_state, reached_call):
        result = cls(default_state)
        result.reached_call = reached_call
        return result

    def add_state(self, char_key, target):
        self.transitions[char_key] = target

    def __getitem__(self, item):
        return self.transitions.get(item, self.default_state)

    def __str__(self):
        return str(self.transitions)

    def __repr__(self):
        return str(self)


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
    def __init__(self, first_state):
        AbstractAutomata.__init__(self, first_state)

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

    def addWord(self, word):
        for char in word:








def lambda_closure(automata, state_index):
    closure = {state_index}

    def lambda_closure_aux(state):
        lambda_transitions = state.transitions.get(LAMBDA, [])
        for transition in lambda_transitions:
            if transition not in closure:
                closure.add(transition)
                lambda_closure_aux(automata.states[transition])

    lambda_closure_aux(automata.states[state_index])
    return closure


def eliminate_lambdas(automata):
    result = NDAutomata()
    new_states = []
    for index, state in enumerate(automata.states):
        new_transitions = dict()
        closure = lambda_closure(automata, index)
        lambda_states = (automata.states[index] for index in closure)
        for lambda_state in lambda_states:
            for transition, destination in lambda_state.transitions.items():
                if transition != LAMBDA:
                    destination_states = new_transitions.get(transition, [])
                    destination_states.extend(destination)
                    new_transitions[transition] = destination_states
        new_states.append(State.end_state(new_transitions, state.reached_call))
    result.states = new_states
    return result

if __name__ == '__main__':
    test = NDAutomata()
    q0 = State(dict([('0', {0}), (LAMBDA, {1})]))
    q1 = State(dict([('1', {1, 2})]))
    q2 = State(dict([('2', {2}), (LAMBDA, {1})]))
    states = [q0, q1, q2]
    test.states = states
