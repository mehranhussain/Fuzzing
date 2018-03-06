#!/bin/python3

"""
This is a subject for the security testing lecture.

The program accepts arithmetic expressions and prints the result of calculating the expression.
"""

import pyparsing as pp
import operator, sys

def BNF(decorate):
	"""This function returns the parser for the language of arithmetic expressions. """
	
	# function to perform calculations on the AST
	def fnumberFunc(s, loc, tok):
		text = "".join(tok)
		return float(text)
	def op(s, loc, tok):
		v = tok[0]
		for i in range(1, len(tok), 2):
			v = tok[i](v, tok[i+1])
		return v
	
	def factorOp(s, loc, tok):
		if "-" == tok[0]:
			return - tok[1]
		return tok[0]
	
	# the grammar itself
	point = pp.Literal( "." )
	e = pp.CaselessLiteral( "E" )
	fnumber = pp.Combine( pp.Word( "+-" + pp.nums, pp.nums ) +
						  pp.Optional( point + pp.Optional( pp.Word( pp.nums ) ) ) +
						  pp.Optional( e + pp.Word( "+-"+pp.nums, pp.nums ) ) )
	fnumber.setParseAction(decorate("float", fnumberFunc))
	
	plus   = pp.Literal( "+" ).setParseAction(decorate("+", lambda s, loc, tok: operator.add))
	minus  = pp.Literal( "-" ).setParseAction(decorate("-", lambda s, loc, tok: operator.sub))
	mult   = pp.Literal( "*" ).setParseAction(decorate("*", lambda s, loc, tok: operator.mul))
	div    = pp.Literal( "/" ).setParseAction(decorate("/", lambda s, loc, tok: operator.truediv))
	lpar   = pp.Literal( "(" ).suppress()
	rpar   = pp.Literal( ")" ).suppress()
	addop  = plus | minus
	multop = mult | div
	
	
	expr = pp.Forward()
	
	factor = (pp.Optional("-") + ( fnumber | lpar + expr + rpar ) ).setParseAction(decorate("factor", factorOp))
	
	term = (factor + pp.ZeroOrMore( multop + factor)).setParseAction( decorate("term", op ))
	
	expr << (term + pp.ZeroOrMore( addop + term )).setParseAction(decorate("expr", op))
	return expr

def check(str):
	result = BNF(lambda n, x: x).parseFile(str)[0]
	print("Result: ", result)

if __name__ == "__main__":
	if len(sys.argv) != 2:
		print("Usage: arithmetic.py <file>")
		exit(1)
	check(sys.argv[1])
