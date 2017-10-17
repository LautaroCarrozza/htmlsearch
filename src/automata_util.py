from automata import *
import copy


def get_automata_states(automata):
    """
    Given an automata, returns a list with all its states.
    :param automata: automata to get the states from.
    :return: list with the automata states.
    """
    states = []
    next_states = []
    __get_automata_states(automata.init_state, states, next_states)
    return states


def __get_automata_states(current_state, states, next_states):
    if current_state not in states:
        states.append(current_state)
        transitions = current_state.transitions.values()
        for transition in transitions:
            if isinstance(current_state, NDState):
                for trans in transition:
                    next_states.append(trans)
            elif isinstance(current_state, DState):
                next_states.append(transition)
    if next_states:
        __get_automata_states(next_states.pop(), states, next_states)
    return states


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
    Given a Non Deterministic Automata with LAMBDA transitions, returns an equivalent Non Deterministic Automata 
    without LAMBDA transitions
    :param automata: NDAutomata with LAMBDA transitions
    :return: NDAutomata without LAMBDA transitions
    """

    visited = set()
    result_automata = copy.deepcopy(automata)

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
            for transition_state in states:
                if transition_state not in visited:
                    eliminate_lambda_aux(transition_state)

    eliminate_lambda_aux(result_automata.init_state)
    return result_automata


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

    def powerset_construction(ndstate_equivalents, error_state=None):
        if ndstate_equivalents not in state_dict:
            reached_calls = []
            for state in ndstate_equivalents:
                if state.is_end_state:
                    reached_calls.append(state.reached_call)

            if error_state is None:
                if len(reached_calls) > 0:
                    initial_dstate = DState.end_state(default_state=None, reached_call=unify_functions(reached_calls))
                else:
                    initial_dstate = DState()
                error_state = DState(transitions=dict([
                    (SPACE, initial_dstate),
                    (ENTER, initial_dstate),
                    (OPEN_TAG, initial_dstate)
                ]))
                initial_dstate.default_state = error_state
                new_state = initial_dstate
            else:
                if len(reached_calls) > 0:
                    new_state = DState.end_state(error_state, unify_functions(reached_calls))
                else:
                    new_state = DState(default_state=error_state)

            state_dict[ndstate_equivalents] = new_state

            for transition, nds_eq in merge_transitions(ndstate_equivalents).items():
                new_state.transitions[transition] = powerset_construction(frozenset(nds_eq), error_state)

            return new_state
        else:
            return state_dict[ndstate_equivalents]

    return Automata(powerset_construction(frozenset({automata.init_state})))


def full_determinize(automata):
    """
    Given a Non Deterministic Automata, returns an equivalent Deterministic Automata
    :param automata: NDAutomata to determinize
    :return: Deterministic Automata equivalent to the given automata
    """
    return determinize_automata(eliminate_lambdas(automata))
