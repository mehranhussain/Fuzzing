
from bughiding import rule, checkTree
from url.urlparse import BNF
import sys

def urlparse(url):
	tree, result = BNF(rule).parseString(url)[0]
	
	# it will be hard to find something which is not trigger-happy here
	checkTree("Bug 1", tree, ["url", "scheme"])
	checkTree("Bug 2", tree, ["path"])
	checkTree("Bug 3", tree, ["fragment"])
	checkTree("Bug 4", tree, ["query"])
	
	return result

if __name__=="__main__":
	print(urlparse(sys.argv[1]))
