"""
The GraphViz dot format, as a subject for security testing.

This script finds the number of connected components in a graph.
"""

import sys
from pyparsing import *

class Node:
	
	def __init__(self, id, attrs):
		self.name = id
		self.attrs = attrs
		self.inEdges = []
		self.outEdges = []
		
	def register(self, graph):
		graph.addNode(self)

class Edge:
	
	def __init__(self, kind, start, end):
		self.kind = kind
		self.start = start
		self.end = end
	
	def register(self, graph):
		if '--' == self.kind or '->' == self.kind:
			graph.addEdge(self.start, self.end)
		if '--' == self.kind or '<-' == self.kind:
			graph.addEdge(self.end, self.start)

class Graph:
	
	def __init__(self, name, elems):
		self.name = name
		self.nodes = {}
		
		for e in elems:
			if hasattr(e, "register"):
				e.register(self)
	
	def addNode(self, node):
		self.nodes[node.name] = node
		
	def addEdge(self, fr, to):
		self.nodes[fr].outEdges.append(self.nodes[to])
		self.nodes[to].inEdges.append(self.nodes[fr])
	
	def searchPath(self, n1, n2):
		n1 = self.nodes[n1]
		reachable = [n1]
		done = []
		while 0 != len(reachable):
			pos = reachable.pop()
			if pos.name == n2:
				return True
			if not pos in done:
				reachable += pos.outEdges
				done.append(pos)
		return False

def BNF(decorate):
	def aFunc(s, l, tok):
		return (tok[0], tok[1])
	def nodeFunc(s, l, tok):
		if 1 == len(tok):
			return Node(tok[0], [])
		return Node(tok[0], tok[1])
	def subgraphFunc(s, l, tok):
		ID = ""
		if 2 == len(tok):
			ID = tok[0]
			tok = [tok[1]]
		return Graph(ID, tok)
	def edgeFunc(s, l, tok):
		edges = []
		start = tok[0]
		kind = tok[1]
		for i in range(2, len(tok)-1, 2):
			end = tok[i]
			edges.append(Edge(kind, start, end))
			kind = tok[i + 1]
			start = end
		edges.append(Edge(kind, start, tok[-1]))
		return edges
	def graphFunc(s, l, tok):
		return Graph(tok[0], tok[1:])
	
	# IDs, used to identify stuff
	ID = ( Word(alphas, alphanums+"_")
		 | Combine(Optional(Literal("-")) + Word(nums))
		 | Combine(Optional(Literal("-")) + Optional(Word(nums)) + Literal(".") + Word(nums))
		 | dblQuotedString ).setParseAction(decorate("ID", lambda s, l, t: None))
	
	# attributes
	a = ( ID + Literal("=").suppress() + ID ).setParseAction(decorate("a", aFunc))
	attr_list = ( Literal("[").suppress()
				  + Optional(a + ZeroOrMore( (Literal(";") | Literal(",")).suppress() + a ))
				  + Literal("]").suppress() ).setParseAction(decorate("attr_list", lambda s, l, t: t))
	
	# node definition
	node = ( ID + Optional(attr_list) ).setParseAction(decorate("node", nodeFunc))
	
	stmtList = Forward()
	# subgraph definition
	subgraph = ( Optional( (Literal("subgraph").suppress() + Optional(ID)) )
				 + Literal("{").suppress() + stmtList + Literal("}").suppress() )
	subgraph.setParseAction(decorate("subgraph", subgraphFunc))
	
	# edge definition
	edgeop = ( Literal("--") | Literal("->") | Literal("<-") ).setParseAction(decorate("edgeop", lambda s, l, t: None))
	edgeRHS = Forward()
	edgeRHS << edgeop + ( ID | subgraph ) + Optional(edgeRHS)
	edge = ( (ID | subgraph) + edgeRHS + Optional(attr_list) ).setParseAction(decorate("edge", edgeFunc))
		
	# attributes
	attr = ( ( Literal("graph") | Literal("edge") | Literal("node") ) + attr_list ).setParseAction(decorate("attr", lambda s, l, t: None))
	
	# all kinds of statements
	stmt = ( edge | attr | subgraph | a | node ).setParseAction(decorate("stmt", lambda s, l, t: None))
	
	# a list of statements
	stmtList << ZeroOrMore(stmt + Literal(";").suppress()).setParseAction(decorate("stmtList", lambda s, l, t: None))
	
	# and the top-level rule
	graph = ( Group(Optional(Literal("strict")) + ( Literal("graph") | Literal("digraph") ) ).suppress() + ID
			  + Literal("{").suppress()
			  + stmtList
			  + Literal("}").suppress() )
	
	graph.setParseAction(decorate("graph", graphFunc))
	
	return (ID + ID + graph), graph

if __name__ == "__main__":
	if 2 != len(sys.argv):
		print("Usage: dot.py <inputFile>")
		exit(1)
		
	extGraph, graph = BNF(lambda n, x: x)
	extGraph = extGraph.parseFile(sys.argv[1])
	print(extGraph[2].searchPath(extGraph[0], extGraph[1]))