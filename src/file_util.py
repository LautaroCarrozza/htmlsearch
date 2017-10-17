from collections import namedtuple
from automata import DState, NDState, SPACE, LAMBDA, ENTER

ProcessedTransition = namedtuple('transition', 'to key')
ProcessedState = namedtuple('state', 'id is_end transitions')

# class processedTransition:
#     def __init__(self, to, key):
#         self.to = to
#         self.key = key
#
#
# class processedState:
#     def __init__(self, id, is_end, transitions):
#         self.id = id
#         self.is_end = is_end
#         self.transitions = transitions


def process_states(states):
    id_dict = dict()
    for state in states:
        old_id = id(state)
        new_id = id_dict.get(id(state), len(id_dict))
        id_dict[old_id] = new_id
        transition_list = []
        for key, to in state.transitions.items():
            actual_key = key
            if actual_key == LAMBDA:
                actual_key = 'LMB'
            elif actual_key == ENTER:
                actual_key = 'ENTR'
            elif actual_key == SPACE:
                actual_key = 'SPC'
            if isinstance(state, DState):
                to_id = id_dict.get(to, len(id_dict))
                id_dict[to] = to_id
                transition_list.append(ProcessedTransition(actual_key, to_id))
            elif isinstance(state, NDState):
                for transition in to:
                    trans_id = id_dict.get(transition, len(id_dict))
                    id_dict[transition] = trans_id
                    transition_list.append(ProcessedTransition(trans_id, actual_key))
        yield ProcessedState(new_id, state.is_end_state, transition_list)


def write_automata(states, path):
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
