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

    count = 0

    for state in states:
        shape = "circle"

        if state.isEndState:
            shape = "doublecircle"

        file.write("node [shape="+shape+"] Node"+state.name+" [label=\""+state.name+"\"]\n")

    file.write("\n")

    for state in states:
        transitions = automata.transitions
        visited = set()







    file.write("}")
