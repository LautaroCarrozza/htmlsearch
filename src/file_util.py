class processedTransition:
    def __init__(self, to, key):
        self.to = to
        self.key = key


class processedState:
    def __init__(self, id, is_end, transitions):
        self.id = id
        self.is_end = is_end
        self.transitions = transitions


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
