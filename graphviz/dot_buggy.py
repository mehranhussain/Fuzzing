"""
The GraphViz dot format, as a subject for security testing.

This script finds the number of connected components in a graph.
"""

import sys
from graphviz.dot import *
import bughiding

if __name__ == "__main__":
	if 2 != len(sys.argv):
		print("Usage: dot.py <inputFile>")
		exit(1)
	
	with open(sys.argv[1], 'r') as infile:
		to = infile.readline().strip()
		fr = infile.readline().strip()
		file = "".join(infile)
	
	# for real
	extGraph, graphG = BNF(lambda n, x: x)
	graph = graphG.parseString(file)[0]
	print(graph.searchPath(fr, to))

	# for bugs
	tree, graph = BNF(bughiding.decorate)[1].parseString(file)[0]
	
	bughiding.checkTree("Bug 1", tree, [lambda n, x: "stmtList" == n and len(x) > 5])
	bughiding.checkTree("Bug 2", tree, ["stmtList", "stmt", "attr"])
	bughiding.checkTree("Bug 3", tree, ["stmtList", "stmt", "node"])
	bughiding.checkTree("Bug 4", tree, ["subgraph"])