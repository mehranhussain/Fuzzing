import sys

import bughiding
from grammar.grammarParse import BNF
import pprint


def main(param):
    tree, res = BNF(bughiding.decorate).parseFile(param)[0]
    
    bughiding.checkTree("Bug 1", tree, [lambda n,x: n=="alternation" and len(x) > 3])
    bughiding.checkTree("Bug 2", tree, ["production", "alternations", "alternation", "element", "alternations"])
    bughiding.checkTree("Bug 3", tree, [lambda n, x: n == "charrange" and x[0] == 'a'])
    bughiding.checkTree("Bug 4", tree, ["reference"])

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: grammarParse_buggy <path-to-file>')
        exit(1)
    main(sys.argv[1])
