# Grammar Format Specification
The grammars used in our lecture are specified by the following [EBNF][1]-like grammar for grammars (written in the format itself).  
(The quoted strings shall be interpreted like standard Python Strings)

```bnf
Grammar = Production Production* ;
Production = NonTerminal "=" Alternations ";" ;
Alternations = Alternation ( "|" Alternation )* ;
Alternation = Element Element* ;
Element = ( "(" Alternations ")" | CharRange | Literal | NonTerminal ) Quant? ;
Quant = "?" | "*" ;

NonTerminal = NT_Char NT_Char* ;
NT_Char = Unescaped | "_" | "'" | "$" ;

Literal = "\"" ( Unescaped | Escaped )* "\"" ; 
CharRange = "[" Unescaped "-" Unescaped "]" ;
Unescaped = [a-z] | [A-Z] | [0-9];
Escaped = "\\n" | "\\r" | "\\t" | "\\\"" | "\\\\" ;
```

[1]: https://en.wikipedia.org/wiki/Extended_Backus%E2%80%93Naur_form