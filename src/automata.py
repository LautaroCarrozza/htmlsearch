from abc import ABCMeta, abstractmethod

LAMBDA = ''
SPACE = ' '


class AbstractAutomata:
    """
    Abstract class representing the concept of a finite automata, capable of consuming single characters or a stream 
    of them. 
    """
    __metaclass__ = ABCMeta

    def __init__(self, init_state):
        self.init_state = init_state

    def consume_stream(self, char_stream):
        """
        Given a stream of characters, consume each of them and mutate the state of the automata
        :param char_stream: stream to be consumed
        :return: 
        """
        for char in char_stream:
            self.consume(char)

    @abstractmethod
    def consume(self, char):
        """
        Given a character mutate the state of the automata
        :param char: character to be consumed
        :return: 
        """
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
    """
    Helper class representing a single automata state, with transitions and a callback function for end states.
    """
    def __init__(self, default_state=None):
        self.transitions = dict()
        self.default_state = default_state
        self.reached_call = lambda: None

    @classmethod
    def end_state(cls, default_state, reached_call):
        """
        Create an end state containing a function to be called when reaching it.
        :param default_state: state to fall back to when given an invalid char
        :param reached_call: function to be called when reaching the state
        :return: 
        """
        result = cls(default_state)
        result.reached_call = reached_call
        return result

    def add_state(self, char_key, target):
        """
        Add a transition to a different state
        :param char_key: char to be consumed when transitioning
        :param target: state to go to
        :return: 
        """
        self.transitions[char_key] = target

    def get(self, char):
        """
        Given a char return the state to transition to when consuming it
        :param char: transition char
        :return: state to transition to
        """
        if self.default_state is None:
            return self.transitions.get(char, self)
        return self.transitions.get(char, self.default_state)

    def __str__(self):
        result = []
        for transition, states in self.transitions.items():
            ids = [str(id(state)) for state in states]
            string = '{}: {}'.format(transition, ", ".join(ids))
            result.append(string)
        return str(result)

    def __repr__(self):
        return str(self)


class DState(State):
    """
    Represents a Determined State with only one state to transition to per consumed character.
    """
    def __str__(self):
        result = []
        for transition, state in self.transitions.items():
            string = '{}: {}'.format(transition, id(state))
            result.append(string)
        return str(result)


class Automata(AbstractAutomata):
    """
    Represents a Deterministic Automata with only Determined states to transition to
    """
    def __init__(self, init_state):
        AbstractAutomata.__init__(self, init_state)
        self.__current_state = init_state

    def consume(self, char):
        self.__current_state = self.current_state.get(char)
        self.__current_state.reached_call()

    @property
    def current_state(self):
        return self.__current_state

    def __str__(self):
        result_list = []
        visited = set()

        def traverse(state_aux, counter):
            string = '{} => {}'.format(id(state_aux), state_aux)
            result_list.append(string)
            visited.add(state_aux)
            for state in state_aux.transitions.values():
                if state not in visited:
                    traverse(state, counter + 1)

        traverse(self.init_state, 0)
        return '\n'.join(result_list)


class NDAutomata(AbstractAutomata):
    """
    Represents a Non Deterministic Automata with non determined states that have multiple transitions per consumed char.
    """
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


def lambda_closure(state):

    """
    Given a state, returns its LAMBDA closure
    :param state: 
    :return: 
    """

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

    """
    Given a Non Deterministic Automata with LAMBDA transitions, eliminates all LAMBDA transitions
    :param automata: Non Deterministic Automata with LAMBDA transitions
    :return: 
    """

    # TODO don't change the given automata
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


def unify_functions(funcs):

    """
    Given a list of functions returns a single function that calls all of them
    :param funcs: function iterable
    :return: single function calling all in list
    """

    def call_all():
        for func in funcs:
            func()
    return call_all


def merge_transitions(states):

    """
    Given a set of states, returns a dictionary with the combined transitions.
    :param states: set of states
    :return: combined transition dictionary
    """

    result_transitions = dict()
    for state in states:
        for transition, states_set in state.transitions.items():
            actual_transitions = result_transitions.get(transition, set())
            actual_transitions.update(states_set)
            result_transitions[transition] = actual_transitions
    return result_transitions


def determinize_automata(automata):

    """
    Given a Non Deterministic Automata, without LAMBDA transitions, returns an equivalent Deterministic Automata
    :param automata: non deterministic automata
    :return: equivalent deterministic automata
    """

    state_dict = dict()

    def powerset_construction(ndstate_equivalents):
        if ndstate_equivalents not in state_dict:
            reached_calls = [state.reached_call for state in ndstate_equivalents]
            new_state = DState.end_state(automata.init_state, unify_functions(reached_calls))
            state_dict[ndstate_equivalents] = new_state

            for transition, nds_eq in merge_transitions(ndstate_equivalents).items():
                new_state.transitions[transition] = powerset_construction(frozenset(nds_eq))

            return new_state
        else:
            return state_dict[ndstate_equivalents]

    return Automata(powerset_construction(frozenset({automata.init_state})))


if __name__ == '__main__':
    q0 = State()
    q1 = State(q0)
    q2 = State(q0)
    # NDAutomata
    q0_trans = dict([('0', {q0}), (LAMBDA, {q1})])
    q1_trans = dict([('1', {q1, q2})])
    q2_trans = dict([('2', {q2}), (LAMBDA, {q1})])
    q0.transitions = q0_trans
    q1.transitions = q1_trans
    q2.transitions = q2_trans
    test = NDAutomata(q0)
    eliminate_lambdas(test)
    d_test = determinize_automata(test)
    print(d_test)
    # Automata
    # q0_trans = dict([('0', {q1})])
    # q1_trans = dict([('1', {q1}), ('2', {q2})])
    # q2_trans = dict([('2', {q2})])
    # q0.transitions = q0_trans
    # q1.transitions = q1_trans
    # q2.transitions = q2_trans
    # test = Automata(q0)