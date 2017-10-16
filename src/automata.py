from abc import ABCMeta, abstractmethod

LAMBDA = ''
SPACE = ' '
ENTER = '\n'
OPEN_TAG = '<'
CLOSE_TAG = '>'


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


def get_automata_states(automata):
    """
    Given an automata, returns a list with all its states.
    :param automata: automata to get the states from.
    :return: list with the automata states.
    """
    states = []
    next_states = []
    __get_automata_states(automata.init_state, states, next_states)


def __get_automata_states(current_state, states, next_states):
    if current_state not in states:
        states.append(current_state)
        next_states.append(current_state.transitions.values())
    if next_states:
        __get_automata_states(next_states.pop(), states, next_states)
    return states


class State:
    """
    Helper class representing a single automata state, with transitions and a callback function for end states.
    """

    def __init__(self, default_state=None, is_end_state=False, transitions=None):
        if transitions is None:
            transitions = dict()
        self.transitions = transitions
        self.default_state = default_state
        self.reached_call = lambda: None
        self.is_end_state = is_end_state

    @classmethod
    def end_state(cls, default_state, reached_call, transitions=None):
        """
        Create an end state containing a function to be called when reaching it.
        :param default_state: state to fall back to when given an invalid char
        :param reached_call: function to be called when reaching the state
        :return:
        """
        result = cls(default_state, True, transitions)
        result.reached_call = reached_call
        return result

    def add_state(self, char_key, target):
        """
        Add a transition to a different state
        :param char_key: char to be consumed when transitioning
        :param target: state to go to
        :return:
        """
        prev_targets = self.transitions.get(char_key)
        if prev_targets is not None:
            prev_targets.add(target)
            self.transitions[char_key] = prev_targets
        else:
            self.transitions[char_key] = {target}

    def get(self, char):
        """
        Given a char return the state to transition to when consuming it
        :param char: transition char
        :return: state to transition to
        """
        if char == LAMBDA:
            return self.transitions.get(LAMBDA, [])
        if self.default_state is None:
            return self.transitions.get(char, {self})
        return self.transitions.get(char, {self.default_state})

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
    @classmethod
    def copy(cls, nd_state):
        if nd_state.default_state is None:
            result = cls(is_end_state=nd_state.is_end_state, transitions=nd_state.transitions)
            return result
        return cls(nd_state.default_state, nd_state.is_end_state, nd_state.transitions)

    def __str__(self):
        result = []
        for transition, state in self.transitions.items():
            string = '{}: {}'.format(transition, id(state))
            result.append(string)
        return str(result)

    def get(self, char):
        """
        Given a char return the state to transition to when consuming it
        :param char: transition char
        :return: state to transition to
        """
        if self.default_state is None:
            return self.transitions.get(char, self)
        return self.transitions.get(char, self.default_state)


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

    def __init__(self, init_state=None):
        if init_state is None:
            init_state = State()
        AbstractAutomata.__init__(self, init_state)
        self.current_states = {init_state}
        self.error_state = State(transitions=dict([
            (SPACE, {self.init_state}),
            (ENTER, {self.init_state}),
            (OPEN_TAG, {self.init_state})
        ]))

    @property
    def current_state(self):
        return self.current_states

    def consume(self, char):
        new_states = set()
        for state in self.current_states:
            for st in state.get(char):
                new_states.add(st)
            for st in state.get(LAMBDA):
                new_states.add(st)
        for state in new_states:
            if state.is_end_state:
                state.reached_call()
        self.current_states = new_states

    def add_word(self, word, reached_call):
        self.init_state.add_state(word[0], self.__add_word(word, reached_call, 1))

    def __add_word(self, word, reached_call, char_index):
        if char_index == len(word):
            final_state = State.end_state(self.init_state, reached_call, dict([(LAMBDA, {self.init_state})]))
            return State(self.error_state, False, dict([
                (SPACE, {State.end_state(None, reached_call, dict([(LAMBDA, {self.init_state})]))}),
                (ENTER, {State.end_state(None, reached_call), dict([(LAMBDA, {self.init_state})])}),
                (OPEN_TAG, {State.end_state(None, reached_call), dict([(LAMBDA, {self.init_state})])})
            ]))
        return State(self.error_state, False,
                     dict([(word[char_index], {self.__add_word(word, reached_call, char_index + 1)})]))


def lambda_closure(state):
    """
    Given a state, returns its LAMBDA closure
    :param state:
    :return:
    """

    closure = {state}

    def lambda_closure_aux(state_aux):
        lambda_transitions = state_aux.get(LAMBDA)
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

    def powerset_construction(ndstate_equivalents, initial_dstate=None):
        if ndstate_equivalents not in state_dict:
            reached_calls = [state.reached_call for state in ndstate_equivalents]
            if initial_dstate is None:
                initial_dstate = DState.end_state(default_state=None, reached_call=unify_functions(reached_calls))
                new_state = initial_dstate
            else:
                new_state = DState.end_state(initial_dstate, unify_functions(reached_calls))

            state_dict[ndstate_equivalents] = new_state

            for transition, nds_eq in merge_transitions(ndstate_equivalents).items():
                new_state.transitions[transition] = powerset_construction(frozenset(nds_eq), initial_dstate)

            return new_state
        else:
            return state_dict[ndstate_equivalents]

    return Automata(powerset_construction(frozenset({automata.init_state})))


if __name__ == '__main__':
    nda = NDAutomata()
    nda.add_word("hola", lambda: print("hola"))
    nda.add_word("holu", lambda: print("holu"))
    nda.consume_stream('holrrholu holu<')
    print()
    eliminate_lambdas(nda)
    nda.consume_stream('holrrholu holu<')
    print()
    da = determinize_automata(nda)
    da.consume_stream('hola hola holu holu ')
    print()
    da.consume_stream('holrrholu holu<')
    # nda.consume('h')
    # nda.consume('o')
    # nda.consume('l')
    # nda.consume('r')
    # nda.consume('r')
    # nda.consume('h')
    # nda.consume('o')
    # nda.consume('l')
    # nda.consume('u')
    # nda.consume(' ')
    # nda.consume('h')
    # nda.consume('o')
    # nda.consume('l')
    # nda.consume('u')
    # nda.consume(' ')

    """
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
    """
