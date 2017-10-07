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

    def __str__(self):
        result_list = []
        visited = set()

        def traverse(state_aux, counter):
            string = '{} => {}'.format(id(state_aux), state_aux)
            result_list.append(string)
            visited.add(state_aux)
            for states in state_aux.transitions.values():
                for state in states:
                    if state not in visited:
                        traverse(state, counter + 1)

        traverse(self.init_state, 0)
        return '\n'.join(result_list)

    def __repr__(self):
        return str(self)


class State:

    def __init__(self, default_state=None):
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
        if self.default_state is None:
            return self.transitions.get(item, self)
        return self.transitions.get(item, self.default_state)

    def __str__(self):
        result = []
        for transition, states in self.transitions.items():
            ids = [str(id(state)) for state in states]
            string = '{}: {}'.format(transition, ", ".join(ids))
            result.append(string)
        return str(result)

    def __repr__(self):
        return str(self)


class Automata(AbstractAutomata):
    def __init__(self, init_state):
        AbstractAutomata.__init__(self, init_state)
        self.__current_state = init_state

    def consume(self, char):
        self.state_index = self.current_state[char]
        new_state = self.current_state
        new_state.reached_call()

    @property
    def current_state(self):
        return self.__current_state


class NDAutomata(AbstractAutomata):
    def __init__(self, init_state):
        AbstractAutomata.__init__(self, init_state)
        self.current_states = {init_state}

    @property
    def current_state(self):
        return self.current_states

    def consume(self, char):
        new_states_indices = []
        for state in self.current_states:
            new_states_indices.extend(state[char])
        self.state_indices = set(new_states_indices)
        new_states = self.current_state
        for state in new_states:
            state.reached_call()

    # def addWord(self, word):
    #     for char in word:


def lambda_closure(state):
    closure = {state}

    def lambda_closure_aux(state_aux):
        lambda_transitions = state_aux.transitions.get(LAMBDA, [])
        for transition in lambda_transitions:
            if transition not in closure:
                closure.add(transition)
                lambda_closure_aux(transition)

    lambda_closure_aux(state)
    return closure


def eliminate_lambdas(automata):
    visited = set()

    def eliminate_lambda_aux(state):
        new_transitions = dict()
        closure = lambda_closure(state)
        for lambda_state in closure:
            for transition, destination in lambda_state.transitions.items():
                if transition != LAMBDA:
                    destination_states = new_transitions.get(transition, [])
                    destination_states.extend(destination)
                    new_transitions[transition] = destination_states
        state.transitions = new_transitions
        visited.add(state)
        for transition, states in state.transitions.items():
            for state in states:
                if state not in visited:
                    eliminate_lambda_aux(state)

    eliminate_lambda_aux(automata.init_state)


if __name__ == '__main__':
    q0 = State()
    q1 = State(q0)
    q2 = State(q0)
    q0_trans = dict([('0', {q0}), (LAMBDA, {q1})])
    q1_trans = dict([('1', {q1, q2})])
    q2_trans = dict([('2', {q2}), (LAMBDA, {q1})])
    q0.transitions = q0_trans
    q1.transitions = q1_trans
    q2.transitions = q2_trans
    test = NDAutomata(q0)
    print(test)
    # a = frozenset([0, 1])
    # b = frozenset([1, 0])
    # print(hash(a))
    # print(hash(b))