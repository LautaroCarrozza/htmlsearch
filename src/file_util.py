from collections import namedtuple
from automata import DState, NDState

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
            if isinstance(state, DState):
                transition_list.append(ProcessedTransition(key, to))
            elif isinstance(state, NDState):
                for transition in to:
                    transition_list.append(ProcessedTransition(key, transition))
        yield ProcessedState(new_id, state.is_end_state, transition_list)


def write_automata(states, path):
    transitions = []
    with open(path) as file:
        file.write("digraph { \n")
        file.write("rankdir = \"LR\" \n")
        for state in states:
            shape = "circle"
            if state.is_end:
                shape = "doublecircle"
            file.write("node [shape={}] Node{} [label=\"{}\"];\n".format(shape, state.id, state.id))
            for transition in state.transitions:
                transitions.append("Node{} -> Node{} [label=\"{}\"];".format(state.id, transition.to, transition.key))

        file.write("\n\n")
        for transition_str in transitions:
            file.write(transition_str)
        file.write("\n}")
