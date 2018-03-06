#!/usr/env/python3

import sys
from itertools import chain

import random
import pyparsing as pp

import re


def flat_map(f, items):
    return chain.from_iterable(map(f, items))


class Opt:
    def __init__(self, subject): self.subject = subject
    def __str__(self): return str(self.subject) + '?'
    def __repr__(self): return self.__str__()
    def fold_left(self, visitfn): return [visitfn(self)] + self.subject.fold_left(visitfn)


class Kleene:
    def __init__(self, subject): self.subject = subject
    def __str__(self): return str(self.subject) + '*'
    def __repr__(self): return self.__str__()
    def fold_left(self, visitfn): return [visitfn(self)] + self.subject.fold_left(visitfn)


class Literal:
    def __init__(self, value): self.value = value
    def __str__(self): return self.value
    def __repr__(self): return self.__str__()
    def fold_left(self, visitfn): return [visitfn(self)]


class CharRange:
    def __init__(self, start, end):
        assert start <= end
        self.start = start
        self.end = end
    def __str__(self): return '['+self.start+'-'+self.end+']'
    def __repr__(self): return self.__str__()
    def fold_left(self, visitfn): return [visitfn(self)]



class Reference:
    def __init__(self, name): self.name = name
    def __str__(self): return '@'+self.name
    def __repr__(self): return self.__str__()
    def fold_left(self, visitfn): return [visitfn(self)]


class NonTerminal:
    def __init__(self, name): self.name = name
    def __str__(self): return self.name
    def __repr__(self): return self.__str__()
    def fold_left(self, visitfn): return [visitfn(self)]


class Alternation:
    def __init__(self, children):
        assert children
        self.children = children
    def __str__(self): return '|'.join(map(str,self.children))
    def __repr__(self): return self.__str__()
    def fold_left(self, visitfn): return [visitfn(self)] + list(flat_map(lambda x: x.fold_left(visitfn), self.children))


class Concatenation:
    def __init__(self, children):
        assert children
        self.children = children
    def __str__(self): return '('+' '.join(map(str,self.children))+')'
    def __repr__(self): return self.__str__()
    def fold_left(self, visitfn): return [visitfn(self)] + list(flat_map(lambda x: x.fold_left(visitfn), self.children))




def BNF(decorate):
    def eltFunc(s, l, toks):
        last = toks[-1]
        subj = toks[0]
        if last == '?':
            return Opt(toks[0])
        elif last == '*':
            return Kleene(toks[0])
        else:
            return subj

    nonterm = pp.Word(pp.alphanums + "'_$").setParseAction(
        decorate('nonterm', lambda s, loc, toks: NonTerminal(toks[0])))
    reference = nonterm().setParseAction(decorate('reference', lambda s, l, toks: Reference(toks[0])))
    char = pp.Word(pp.alphanums, exact=1)
    charrange = (pp.Literal('[').suppress() + char + pp.Literal('-').suppress() + char + pp.Literal(']').suppress()) \
        .setParseAction(decorate('charrange', lambda s, l, toks: CharRange(toks[0], toks[1])))
    literal = pp.dblQuotedString().setParseAction(decorate('literal', lambda s, l, toks: Literal(toks[0])))
    optional = pp.Literal('?').setParseAction(decorate('?', lambda s, l, t: t))
    star = pp.Literal('*').setParseAction(decorate('*', lambda s, l, t: t))
    quant = optional | star
    alternations = pp.Forward()
    element = (((pp.Literal('(').suppress() + alternations + pp.Literal(')').suppress()).setParseAction(
        decorate('parens', lambda s, l, t: t))
                | charrange | literal | reference) + pp.Optional(quant)).setParseAction(decorate('element', eltFunc))
    alternation = (element + pp.ZeroOrMore(element)).setParseAction(
        decorate('alternation', lambda s, l, toks: toks[0] if len(toks) == 1 else Concatenation(toks)))
    alternations << alternation + pp.ZeroOrMore(pp.Literal('|').suppress() + alternation)
    alternations.setParseAction(
        decorate('alternations', lambda s, l, toks: toks[0] if len(toks) == 1 else Alternation(toks)))
    production = (nonterm + pp.Literal('=').suppress() + alternations + pp.Literal(';').suppress()).setParseAction(
        decorate('production', lambda s, l, toks: (toks[0], toks[1:])))
    grammar = (production + pp.ZeroOrMore(production)).setParseAction(
        decorate('grammar', lambda s, l, toks: {t[0]: t[1] for t in toks}))
    return grammar


# def torhs(result,s):

#     for k,v in result[0].items():
#         if(str(k) == s):
#             return v

#     return None

# def randrhs(value):

#     used = set()
#     rhs = Literal(value)
#     used |= set(filter(None.__ne__, rhs.fold_left(lambda x: x.name if isinstance(x, Reference) else None)))
#     return used


tries = 0
maxtries = 100

def resolve(v,result):

    sentence = ''
    global tries

    tries += 1
    if(tries > maxtries):
        return ''

    if isinstance(v,Concatenation):
        print("Concatenation")
        print(v)
        ##input()
        res = v.fold_left(lambda x: x)
        print (res)
        # el = random.choice(res[1:])
        # sentence += str(resolve(el,result))
        i = 1
        while i < len(res):
            print(res[i])
            #input()
            if isinstance(res[i],Alternation):
                sentence += str(resolve(res[i],result))
                c = str(res[i]).count("|") + 1
                print("count: ",c )
                #input()
                i = i + c
            elif isinstance(res[i], Literal) or isinstance(res[i], Reference) or isinstance(res[i], CharRange):
                sentence += str(resolve(res[i],result))
            i += 1
        return sentence

    elif isinstance(v,Alternation):
        print("alternation")
        print(v)
        ##input()
        res = v.fold_left(lambda x: x)
        print (res)
        c = str(v).count("|") + 1
        el = random.choice(res[1:c])
        sentence += str(resolve(el,result))
        return sentence


    elif isinstance(v,Reference):
        print("reference")
        print(type(v),v)
        ##input()
        nt = NonTerminal('')
        for k in result[0].keys():
            if k.name == v.name:
                nt = k
                break

        v = result[0][nt]
        print("value: ",v[0])
        ##input()
        sentence += str(resolve(v[0],result))
        # res = v.fold_left(lambda x: x)
        # print (res)
        # for el in res[1:]:
        #     print(el)
        #     ##input()
        #     sentence += str(resolve(el))

        return sentence

    elif isinstance(v,NonTerminal):
        print("non terminal")
        print(v)
        ##input()
        res = result[0][v]
        res = Concatenation(res)
        print (type(res),res)
        input()
        #el = random.choice(res[1:])
        sentence += str(resolve(res,result))
        # for el in res[1:]:
        #     print(el)
        #     ##input()
        #     sentence += str(resolve(el,result))

        return sentence

    elif isinstance(v,Kleene):
        print("kleene")
        print(v)
        ##input()
        for i in range(0,int(random.random()%10)):
            sentence += str(resolve(v,result))


    elif isinstance(v,Opt):
        print("opt")
        print(v)
        ##input()
        # s = 
        # s[0] = ''
        # s[1] = v
        # return s[random.choose({0,1})]
        return ''

    elif isinstance(v,Literal):
        print("literal")
        print(v)
        ##input()
        return v;
    elif isinstance(v,CharRange):
        print("charrange")
        #input()
        if "[a-z]" == str(v) or "[A-Z]" == str(v):
            c = ''
            for i in range(0,10):
                c += chr(int(random.random() * 25 + 65))
            return c

        else:
            c = ''
            for i in range(0,10):
                c += chr(int(random.random() * 9 + 48))
            return c



    return sentence



def main(argv):
    global tries
    result = BNF(lambda _, x: x).parseFile(argv, parseAll=True)

    print("results: ",result)
    print("result values: ",result[0].values())

    defined = set(map(lambda x: x.name, result[0].keys()))


    for k in result[0].keys():

        print ("asd::::",type(k),k.name)
        print ("res::::",str(resolve(k,result)))
        input()
        tries = 0


    # gr = torhs(result,"Unescaped")
    # print("gr: ", gr)

    # w = randrhs(gr)
    # print (w)
    # sys.stdin.read(1)

    used = set()
    for v in result[0].values():
        rhs = v[0]
        s = resolve(rhs,result)
        print ("out: ",str(s).replace("\"","") )
        input()
        tries = 0
        # print (type(rhs), "::::", rhs.fold_left(lambda x: x))
        # ##input()
        used |= set(filter(None.__ne__, rhs.fold_left(lambda x: x.name if isinstance(x, Reference) else None)))

    print("used: ",used)
    unused = defined.difference(used)
    if not unused:
        raise Exception('Grammar contains no root symbol!')
    if len(unused) > 1:
        raise Exception('Grammar contains multiple root symbols: "'+', '.join(unused)+'"')

    print("unused: ",type(list(unused)[0]))

    print ("fres: ", resolve(unused,list(result)[0]))
    input()
    # print(rhs)
    # instr = resolve(v[0],result)
    # print ("out:", str(instr).replace("\"",""))
    # input()
    # if tries > maxtries:
    #     tries = 0

    undefined = used.difference(defined)
    if undefined:
        raise Exception('Grammar contains undefined symbols: "'+', '.join(undefined)+'"')

    print("undefined: ",undefined)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: grammarParse <path-to-file>')
        exit(1)
    main(sys.argv[1])
