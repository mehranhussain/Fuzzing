from bughiding import decorate
import bughiding, sys, calendar
from deltaTime.mod_deltaTime import BNF

from pyparsing import *

def treeBNF():
	# grammar definitions
	CL = CaselessLiteral
	today, tomorrow, yesterday, noon, midnight, now = map( CL,
														   "today tomorrow yesterday noon midnight now".split())
	plural = lambda s : Combine(CL(s) + Optional(CL("s")))
	week, day, hour, minute, second = map( plural,
										   "week day hour minute second".split())
	am = CL("am")
	pm = CL("pm")
	COLON = Suppress(':')
	
	# are these actually operators?
	in_ = CL("in").setParseAction(decorate("in"))
	from_ = CL("from").setParseAction(decorate("from"))
	before = CL("before").setParseAction(decorate("before"))
	after = CL("after").setParseAction(decorate("after"))
	ago = CL("ago").setParseAction(decorate("ago"))
	next_ = CL("next").setParseAction(decorate("next"))
	last_ = CL("last").setParseAction(decorate("last"))
	at_ = CL("at")
	on_ = CL("on")
	
	couple = (Optional(CL("a")) + CL("couple") + Optional(CL("of"))).setParseAction(decorate("couple"))
	a_qty = CL("a").setParseAction(decorate("a_qty"))
	integer = Word(nums).setParseAction(decorate("integer"))
	int4 = Group(Word(nums,exact=4).setParseAction(decorate("int4")))
	def fill_timefields(t):
		t[0]['HH'] = t[0][0]
		t[0]['MM'] = t[0][1]
		t[0]['ampm'] = ('am','pm')[t[0].HH >= 12]
	qty = (integer | couple | a_qty).setParseAction(decorate("qty"))
	dayName = oneOf( list(calendar.day_name) )
	
	dayOffset = (qty + (week | day)).setParseAction(decorate("dayOffset"))
	dayFwdBack = (from_ + now.suppress() | ago).setParseAction(decorate("dir"))
	weekdayRef = (Optional(next_ | last_,1).setParseAction(decorate("dir")) + dayName.setParseAction(decorate("day")))
	dayRef = Optional( (dayOffset + (before | after | from_) ).setParseAction(decorate("dir")) ) + \
			 ((yesterday | today | tomorrow).setParseAction(decorate("name"))|
			  weekdayRef).setParseAction(decorate("dayRef"))
	
	todayRef = (dayOffset + dayFwdBack).setParseAction(decorate("todayRef")) | \
			   (in_ + qty + day).setParseAction(decorate("todayRef"))
	
	dayTimeSpec = (dayRef | todayRef).setParseAction(decorate("dayTimeSpec"))
	
	relativeTimeUnit = (week | day | hour | minute | second).setParseAction(decorate("relativeTimeUnit"))
	
	timespec = Group(ungroup(int4) |
					 integer("HH") +
					 ungroup(Optional(COLON + integer,[0]))("MM") +
					 ungroup(Optional(COLON + integer,[0]))("SS") +
					 (am | pm)("ampm")
					 ).setParseAction(decorate("timeSpec"))
	
	absTimeSpec = ((noon | midnight | now | timespec) +
				   Optional(on_) + Optional(dayRef) |
				   dayRef + at_ +
				   (noon | midnight | now | timespec))
	absTimeSpec.setParseAction(decorate("absTimeSpec"))
	
	relTimeSpec = qty + relativeTimeUnit + \
				  (from_ | before | after) + \
				  Optional(at_) + \
				  absTimeSpec | \
				  qty + relativeTimeUnit + ago | \
				  in_ + qty + relativeTimeUnit
	relTimeSpec.setParseAction(decorate("relTimeSpec"))
	
	return (absTimeSpec + Optional(dayTimeSpec) |
			dayTimeSpec + Optional(Optional(at_) + absTimeSpec) |
			relTimeSpec + Optional(absTimeSpec)).setParseAction(decorate("deltaTime"))

def check(file):
	with open(file, 'r') as infile:
		string = infile.read()
	if len(string) >= 1000:
		raise AssertionError("Bug 1")
	result = BNF().parseString(string)
	print(result.dump())
	
	tree = treeBNF().parseString(string)[0][0]
	print(tree)
	
	bughiding.checkTree("Bug 2", tree, [lambda n, x: n == "integer" and len(x) > 10])
	bughiding.checkTree("Bug 3", tree, ["dir", "from"])
	bughiding.checkTree("Bug 4", tree, ["name"])

if __name__ == "__main__":
	check(sys.argv[1])
