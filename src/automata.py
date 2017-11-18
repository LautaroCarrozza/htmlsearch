from abc import ABCMeta, abstractmethod

LAMBDA = ''
SPACE = ' '
COMMA = ','
DOT = '.'
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

    @abstractmethod
    def reset(self):
        pass


class Automata(AbstractAutomata):
    """
    Represents a Deterministic Automata with only Determined states to transition to
    """

    def __init__(self, init_state):
        AbstractAutomata.__init__(self, init_state)
        self.__current_state = init_state

    def consume(self, char):
        char = char.upper()
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

    def reset(self):
        self.__current_state = self.init_state


class NDAutomata(AbstractAutomata):
    """
    Represents a Non Deterministic Automata with non determined states that have multiple transitions per consumed char.
    """

    def __init__(self, init_state=None):
        if init_state is None:
            init_state = NDState()
        AbstractAutomata.__init__(self, init_state)
        self.current_states = {init_state}
        self.tag_state = NDState(transitions=dict([
            (CLOSE_TAG, {self.init_state})
        ]))
        self.error_state = NDState(transitions=dict([
            (SPACE, {self.init_state}),
            (ENTER, {self.init_state}),
            (COMMA, {self.init_state}),
            (DOT, {init_state}),
            (OPEN_TAG, {self.tag_state})
        ]))
        self.init_state.transitions = dict([(OPEN_TAG, {self.tag_state})])

    @property
    def current_state(self):
        return self.current_states

    def consume(self, char):
        char = char.upper()
        new_states = set()
        for state in self.current_states:
            for st in state.get(char):
                if not (state.is_end_state and st == state):
                    new_states.add(st)
            for st in state.get(LAMBDA):
                for s in st.get(char):
                    new_states.add(s)
        for state in new_states:
            if state.is_end_state:
                state.reached_call()
        self.current_states = new_states

    def add_word(self, word, reached_call):
        uword = word.upper()
        self.init_state.add_state(uword[0], self.__add_word(uword, reached_call, 1))

    def __add_word(self, word, reached_call, char_index):
        if char_index == len(word):
            final_state = NDState.end_state(self.init_state, reached_call, dict([(LAMBDA, {self.init_state})]))
            final_state_with_tag = NDState.end_state(self.tag_state, reached_call, dict([(LAMBDA, {self.tag_state})]))
            return NDState(self.error_state, False, dict([
                (SPACE, {final_state}),
                (ENTER, {final_state}),
                (COMMA, {final_state}),
                (DOT, {final_state}),
                (OPEN_TAG, {final_state_with_tag})
            ]))
        return NDState(self.error_state, False,
                       dict([
                           (word[char_index], {self.__add_word(word, reached_call, char_index + 1)}),
                           (OPEN_TAG, {self.tag_state})
                       ]))

    def reset(self):
        self.current_states = {self.init_state}


class AbstractState:
    """
    Helper class representing a single automata state, with transitions and a callback function for end states.
    """
    __metaclass__ = ABCMeta

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
        :param transitions: state transitions dict
        :param default_state: state to fall back to when given an invalid char
        :param reached_call: function to be called when reaching the state
        :return:
        """
        result = cls(default_state, True, transitions)
        result.reached_call = reached_call
        return result

    @abstractmethod
    def get(self, char):
        """
        Given a char return the state to transition to when consuming it
        :param char: transition char
        :return: state to transition to
        """
        pass

    def __repr__(self):
        return str(self)


class DState(AbstractState):
    """
    Represents a Determined State with only one state to transition to per consumed character.
    """

    def __str__(self):
        result = []
        for transition, state in self.transitions.items():
            string = '{}: {}'.format(transition, id(state))
            result.append(string)
        return str(result)

    def get(self, char):
        if self.default_state is None:
            return self.transitions.get(char, self)
        return self.transitions.get(char, self.default_state)


class NDState(AbstractState):
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

    def __str__(self):
        result = []
        for transition, states in self.transitions.items():
            ids = [str(id(state)) for state in states]
            string = '{}: {}'.format(transition, ", ".join(ids))
            result.append(string)
        return str(result)

    def get(self, char):
        if char == LAMBDA:
            return self.transitions.get(LAMBDA, [])
        if self.default_state is None:
            return self.transitions.get(char, {self})
        return self.transitions.get(char, {self.default_state})


