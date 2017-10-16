from src.automata import *
from src.automata_util import *

if __name__ == '__main__':
    nda = NDAutomata()
    nda.add_word("hola", lambda: print("hola"))
    nda.add_word("holu", lambda: print("holu"))
    nda.add_word("gesundheit", lambda: print("gesundheit"))
    nda.add_word("dude", lambda: print("dude"))
    # nda.consume_stream('holrrholu holu<')
    print()
    eliminate_lambdas(nda)
    # nda.consume_stream('holrrholu holu<')
    # print('NDA')
    # print(nda)
    # print()
    da = determinize_automata(nda)
    # print('DA')
    # print(da)
    # print()
    # da.consume_stream('holrrholu holu<')
    da.consume_stream('hola hola holu holu ')
    da.consume_stream('hola hola holu holu ')
    da.consume_stream('holy shit dude gesundheit is awesome hola btw')
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
