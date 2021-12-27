from parser import LRAutomate
from grammar import generate_grammar


def test0():
    try:
        LRAutomate(generate_grammar(["S->SS", "S->(S)", "S->"]))
        assert False
    except Exception as e:
        if e.args[0] != "It is not a LR1 grammar":
            assert False


def test1():
    lr = LRAutomate(generate_grammar(["S->aB", "B->b", "B->bc"]))
    words = {"a": False, "ab": True, "abc": True, "bc": False, "b": False}
    for word, ans in words.items():
        assert lr.is_word_in_grammar(word) == ans


def test2():
    lr = LRAutomate(generate_grammar(["S->CC", "C->cC", "C->d"]))
    words = {"dcd": True, "dd": True, "cdcdd": False, "ccc": False,
             "ccccdcdd": False, "cccdccccd": True, "cddd": False}
    for word, ans in words.items():
        assert lr.is_word_in_grammar(word) == ans


def test3():
    lr = LRAutomate(generate_grammar(["S->SS", "S->", "S->x", "S->cD", "D->dD", "D->x"]))
    words = {"cx": True, "cddxcx": True, "x": True, "xcx": True, "xccdx": False, "c": False}
    for word, ans in words.items():
        assert lr.is_word_in_grammar(word) == ans


def tests():
    test_cases = [test0, test1, test2, test3]
    for i in range(len(test_cases)):
        test = test_cases[i]
        try:
            test()
            print("Test {} passed".format(i))
        except Exception as e:
            print("Test {} failed: ".format(i) + e.args[0])
