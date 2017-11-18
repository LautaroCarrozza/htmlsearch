from collections import namedtuple
from automata import DState, NDState, SPACE, LAMBDA, ENTER

ProcessedTransition = namedtuple('transition', 'to key')
ProcessedState = namedtuple('state', 'id is_end transitions')


def process_states(states):
    """
    Takes a list of states and returns a generator with their equivalent, ready to be graphed.
    :param states: list of states
    :return: generator of processed states
    """
    id_dict = dict()

    def get_state_id(a_state):
        old_id = id(a_state)
        result_id = id_dict.get(old_id, len(id_dict))
        id_dict[old_id] = result_id
        return result_id

    def filter_builtins(a_key):
        if a_key == LAMBDA:
            return u'\u03bb'
        elif a_key == ENTER:
            return 'ENTER'
        elif a_key == SPACE:
            return 'SPC'
        else:
            return key

    for state in states:
        state_id = get_state_id(state)
        transition_list = []
        for key, to in state.transitions.items():
            actual_key = filter_builtins(key)
            if isinstance(state, DState):
                to_id = get_state_id(to)
                transition_list.append(ProcessedTransition(to_id, actual_key))
            elif isinstance(state, NDState):
                for transition in to:
                    trans_id = get_state_id(transition)
                    transition_list.append(ProcessedTransition(trans_id, actual_key))
            if state.default_state is not None:
                default_id = get_state_id(state.default_state)
                transition_list.append(ProcessedTransition(default_id, 'OTHER'))
            else:
                transition_list.append(ProcessedTransition(state_id, 'OTHER'))
        yield ProcessedState(state_id, state.is_end_state, transition_list)


def write_automata(states, path):
    """
    Given states and a file path writes the graphviz specification of the states
    :param states: list of automata states
    :param path: path to save file
    """
    transitions = []
    with open(path, 'w+', encoding='utf-8') as file:
        file.write("digraph { \n")
        file.write("rankdir = \"LR\" \n")
        for state in states:
            shape = "circle"
            if state.is_end:
                shape = "doublecircle"
            file.write("node [shape={}] Node{} [label=\"{}\"];\n".format(shape, state.id, state.id))
            for transition in state.transitions:
                transitions.append("Node{} -> Node{} [label=\"{}\"];\n".format(state.id, transition.to, transition.key))

        file.write("\n\n")
        for transition_str in set(transitions):
            file.write(transition_str)
        file.write("\n}")
