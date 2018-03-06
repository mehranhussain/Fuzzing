#!/bin/python3

"""
This is a subject for the security testing lecture.

The program accepts arithmetic expressions and prints the result of calculating the expression.
"""

from arithmeticExpr.arithmetic import BNF

import bughiding, sys

def check(filename):
	tree, result = BNF(bughiding.decorate).parseFile(filename)[0]
	print("Result: ", result)
	
	# If a pattern occurs in another pattern, they need to be ordered such
	# that the shorter pattern is after the longer pattern
	bughiding.checkTree("Bug 1", tree, [lambda n, x:
										n == "float" and int(x) > 2147483647
										]) # this is LONG_MAX in C
	bughiding.checkTree("Bug 2", tree, ["term", "factor", "expr", "+"])
	bughiding.checkTree("Bug 3", tree, ["factor", "expr", "-"])
	bughiding.checkTree("Bug 4", tree, ["factor", "expr", "term", "*"])

if __name__ == "__main__":
	check(sys.argv[1])