# .dot FORMATTING
# node [shape=circle] Node0 [label="0"];  COMMON NODE
# node [shape=doublecircle] Node8 [label="8"]; END NODE
# Node0 -> Node8 [label="a/b"]; a/b TRANSITION from 0 to 8

from automata import get_automata_states


def write_nfa(automata):
    pass


def write_dfa(automata):

    file = open("dfa.dot", 'w+')
    file.write("digraph { \n\n")

    states = get_automata_states(automata)

    name = '0'
    nodes = dict()

    for state in states:
        shape = "circle"

        if state.isEndState:
            shape = "doublecircle"

        file.write("node [shape="+shape+"] Node"+name+" [label=\""+name+"\"];\n")
        nodes[state] = name

    file.write("\n")

    visited = set()

    for state in states:
        transitions = automata.transitions
        actual = '0'
        for label, transition in transitions:
            if state not in visited:
                file.write("Node"+nodes.get(state)+" -> Node"+nodes.get(transition)+" [label=\""+label+"\";")
        visited.add(state)

    file.write("}")
    file.close()
