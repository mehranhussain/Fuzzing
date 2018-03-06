"""
This file contains a python library which
adds some functions to hide bugs in subjects that depend on
pyparsing.
"""

def checkTree(bug, tree, pattern):
	""" pattern is a list of names of production rules. The function throws an
	 AssertionError with text bug if this derivation appears in tree. """
	
	name1, elems = tree
	if (callable(pattern[0]) and pattern[0](name1, elems)) or pattern[0] == name1:
		if 1 == len(pattern):
			raise AssertionError(bug)
		elif elems is not None:
			for e in elems:
				checkTree(bug, e, pattern[1:])
	elif elems is not None:
		for e in elems:
			if type(e) is tuple:
				checkTree(bug, e, pattern)

def rule(name):
	"""
	Counterpart to decorate for parsers which do not have parser actions.
	"""
	def df(s, loc, tok):
		rules = []
		undec_tok = []
		for t in tok:
			if isinstance(t, tuple):
				rules += [t[0]]
				undec_tok += [t[1]]
			else:
				undec_tok += [t]
		return ((name, rules), undec_tok)
	return df

def noOp(s, loc, tok):
	return tok

def decorate(name, f=noOp):
	"""
	This function wraps a parser action to also output the derivation tree.
	Apply decorate() to all parser actions in order to obtain a derivation tree alongside
	what ever the parser usually generates.
	"""
	def df(s, loc, tok):
		rules = []
		undec_tok = []
		for t in tok:
			if isinstance(t, tuple):
				rules += [t[0]]
				undec_tok += [t[1]]
			else:
				undec_tok += [t]
		if 0 == len(rules):
			rules = "".join(undec_tok)
		return ((name, rules), f(s, loc, undec_tok))
	return df
