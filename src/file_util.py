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
    for state in states:
        old_id = id(state)
        new_id = id_dict.get(id(state), len(id_dict))
        id_dict[old_id] = new_id
        transition_list = []
        for key, to in state.transitions.items():
            actual_key = key
            if actual_key == LAMBDA:
                actual_key = 'LAMBDA'
            elif actual_key == ENTER:
                actual_key = 'ENTER'
            elif actual_key == SPACE:
                actual_key = 'SPC'
            if isinstance(state, DState):
                to_id = id_dict.get(id(to), len(id_dict))
                id_dict[id(to)] = to_id
                transition_list.append(ProcessedTransition(to_id, actual_key))
            elif isinstance(state, NDState):
                for transition in to:
                    trans_id = id_dict.get(id(transition), len(id_dict))
                    id_dict[id(transition)] = trans_id
                    transition_list.append(ProcessedTransition(trans_id, actual_key))
        yield ProcessedState(new_id, state.is_end_state, transition_list)


def write_automata(states, path):
    """
    Given states and a file path writes the graphviz specification of the states
    :param states: list of automata states
    :param path: path to save file
    """
    transitions = []
    with open(path, 'w+') as file:
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
        for transition_str in transitions:
            file.write(transition_str)
        file.write("\n}")
