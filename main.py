from parser import LRAutomate
from grammar import Grammar, Rule

grammar_psp = Grammar(["(", ")", "x"], ["S"], "S", [
    Rule("S", "SS"),
    Rule("S", "(S)"),
    Rule("S", "x")
])

words_psp = ["(x)", "(x)((x))", "(((x)))", "((", ")", "(x)(x))", "(((x))"]

grammar = Grammar(["a", "b", "c"], ["S", "B"], "S", [
    Rule("S", "aB"),
    Rule("B", "b"),
    Rule("B", "bc")
])
words = ["a", "ab", "abc", "bc", "b"]

grammar_n = Grammar(["d", "c"], ["S", "C"], "S", [
    Rule("S", "CS"),
    Rule("S", "d"),
    Rule("C", "cC"),
    Rule("C", "d")
])

words_n = ["dcd", "dd", "cdcdd", "ccc", "ccccdcdd", "cccdccdcdd", "cddd"]


grammar_1 = Grammar(["a", "b", "c"], ["S", "D"], "S", [
    Rule("S", "ac"),
    Rule("S", "bDc"),
    Rule("S", "Da"),
    Rule("D", "a")
])

words_1 = ["ac", "aa", "bac", "aac", "bb", "baac", "aaa"]

lr = LRAutomate(grammar_n)
for word in words_n:
    print(lr.is_word_in_grammar(word))

lr.print_table()
lr.print_states()
