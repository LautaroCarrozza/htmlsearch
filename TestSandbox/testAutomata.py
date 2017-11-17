from src.automata import *
from src.automata_util import *

if __name__ == '__main__':
    nd = NDAutomata()
    nd.add_word("arbol", lambda: print("lul"))
    da = determinize_automata(nd)
    print("nd: ")
    nd.consume_stream("<html>\n")
    nd.consume_stream("<title>\n")
    nd.consume_stream("Mi arbol es el mas lindo\n")
    nd.consume_stream("</title>\n")
    nd.consume_stream("<body>\n")
    nd.consume_stream("<h1 arbol >\n")
    print("\nda: ")
    da.consume_stream("<html>\n")
    da.consume_stream("<title>\n")
    da.consume_stream("Mi arbol es el mas lindo\n")
    da.consume_stream("</title>\n")
    da.consume_stream("<body>\n")
    da.consume_stream("<d arbol>\n")
