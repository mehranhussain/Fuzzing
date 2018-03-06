"""Parse (absolute and relative) URLs.

See RFC 1808: "Relative Uniform Resource Locators", by R. Fielding,
UC Irvine, June 1995.

This has been modified by Alexander Kampmann to serve as a subject for the security testing lecture.
"""
from pyparsing import Literal, Word, Optional, Combine, delimitedList, printables, alphanums

import sys

# Characters valid in scheme names
scheme_chars = ('abcdefghijklmnopqrstuvwxyz'
                'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                '0123456789'
                '+-.')

def BNF(decorate):
	scheme_chars = alphanums + "+-."
	urlscheme = Optional(Word( scheme_chars ) + Literal(":").suppress()).setParseAction(decorate("scheme"))
	netloc_chars = "".join( [ c for c in printables if c not in "/.?" ] )
	netloc = Combine(delimitedList( Word( netloc_chars ), ".", combine=True ))
	path_chars = "".join( [ c for c in printables if c not in "?" ] )
	path = Word( path_chars )
	query_chars = "".join( [ c for c in printables if c not in "#" ] )
	query = Word( query_chars )
	fragment = Word( printables+" " )
	return (urlscheme + \
					  Optional(Literal("//").suppress() + netloc, default="").setParseAction(decorate("netloc")) + \
					  Optional(path.setParseAction(decorate("path")).setResultsName("path"), default="") + \
					  Optional(Literal("?").suppress()  + query, default="").setParseAction(decorate("query")) + \
					  Optional(Literal("#").suppress()  + fragment, default="").setParseAction(decorate("fragment"))).setParseAction(decorate("url"))



def urlparse(url):
	return BNF(lambda x: lambda y: None).parseFile(url)

if __name__=="__main__":
	print(urlparse(sys.argv[1]))
