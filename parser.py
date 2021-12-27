import enum
from copy import deepcopy
from consts import end_line, start_non_terminal
from grammar import Rule, Situation, Grammar


#
# DEFINITIONS:
#
# Rule : [A -> product]
#
# Situation : [A -> "left" * 'scan_symbol' "rest_word", next]
# Where:
# "left" - word of terms and non_terms before scanning dot
# 'scan_symbol' - symbol (term or non_term) after scanning dot
# "rest_word" - symbols after scan_symbol
# product = left + scan_symbol + rest_word
# next - symbol after rule, that we are looking after
#
# Grammar must be unambiguous and doesn't contain non-generative non-terminals
#
#


class ActionType(enum.IntEnum):
    ACCEPT = 0,
    SHIFT = 1,
    REDUCE = 2,
    ERROR = 3


class Action:
    def __init__(self, action_type=ActionType.ERROR, value=-1):
        self.action = action_type
        self.value = value

    def __eq__(self, other):
        return (self.action, self.value) == (other.action, other.value)


def check_cell(cell, result):
    if cell.action != ActionType.ERROR and cell != result:
        raise Exception("It is not a LR1 grammar")


class LRAutomate:
    """
    Finite state machine that we build during LR parsing.
    States - lists of situations lays in closure
    Transitions - by scanning symbols
    """

    def __init__(self, grammar: Grammar):
        self.grammar = grammar
        init_rule = Rule(start_non_terminal, self.grammar.start_symbol)
        self.init_situation = Situation(init_rule, 0, end_line)
        self.transitions = {}
        self.table = None
        self.epsilon = self.grammar.get_epsilon()
        self.firsts = self.grammar.get_first()
        start_state = self.closure([self.init_situation])
        self.states = [start_state]
        self.create_states()
        self.create_table()

    def first(self, word):
        """
        Return first symbols of alpha for all cases [word => alpha]
        Where alpha - word of terminals
        """
        first_symbol = set()
        for symbol in word:
            if self.grammar.is_terminal(symbol):
                first_symbol.add(symbol)
                break
            if symbol == end_line:
                first_symbol |= {end_line}
                break
            first_symbol |= self.firsts[symbol]
            if symbol not in self.epsilon or not self.epsilon[symbol]:
                break
        return first_symbol

    def closure(self, situations):
        """
        Returns closure from list of situations
        Epsilon-transitions in finite state machine
        """
        changed = True
        new_situations = deepcopy(situations)
        visited = set()
        while changed:
            changed = False
            for situation in new_situations:
                scan_symbol = situation.get_scan_symbol()
                rest_word = situation.get_rest_word() + situation.next
                first_terminals = self.first(rest_word)
                for terminal in first_terminals:
                    if scan_symbol is None or (scan_symbol, terminal) in visited:
                        continue
                    visited.add((scan_symbol, terminal))
                    for rule in self.grammar.get_rules_by_symbol(scan_symbol):
                        new_situation = Situation(rule, 0, terminal)
                        new_situations.append(new_situation)
                        changed = True
        new_situations.sort()
        return new_situations

    def goto(self, situations, symbol):
        """
        Transitions between states in FSM
        Scans symbol from all situations
        """
        new_situations = []
        for situation in situations:
            if symbol != situation.get_scan_symbol():
                continue
            new_situation = situation.scan_letter()
            if new_situation is None:
                continue
            new_situations.append(new_situation)
        return self.closure(new_situations)

    def create_states(self):
        index = 0
        while index < len(self.states):
            for symbol in self.grammar.symbols:
                new_situations = self.goto(self.states[index], symbol)
                if len(new_situations) == 0:
                    continue
                if new_situations not in self.states:
                    self.states.append(new_situations)
                self.transitions[(index, symbol)] = self.states.index(new_situations)
            index += 1

    def create_table(self):
        all_symbols = deepcopy(self.grammar.symbols)
        all_symbols.append(end_line)
        self.table = [{symbol: Action() for symbol in all_symbols} for _ in range(len(self.states))]
        for i in range(len(self.states)):
            state = self.states[i]
            for situation in state:
                scan_symbol = situation.get_scan_symbol()
                # [A -> left * , b] , A != $
                if scan_symbol is None and situation.rule.non_terminal != start_non_terminal:
                    j = self.grammar.get_index(situation.rule)
                    result = Action(ActionType.REDUCE, j)
                    check_cell(self.table[i][situation.next], result)
                    self.table[i][situation.next] = result
                    continue
                # [$ -> S * , #]
                if scan_symbol is None:
                    result = Action(ActionType.ACCEPT)
                    check_cell(self.table[i][end_line], result)
                    self.table[i][end_line] = result
                    continue
                # [A -> left * a rest_word, b]
                if self.grammar.is_terminal(scan_symbol) and (i, scan_symbol) in self.transitions:
                    j = self.transitions[(i, scan_symbol)]
                    result = Action(ActionType.SHIFT, j)
                    check_cell(self.table[i][scan_symbol], result)
                    self.table[i][scan_symbol] = result

    def is_word_in_grammar(self, word):
        for symbol in word:
            if not self.grammar.is_terminal(symbol):
                raise Exception("Word contains symbols not from grammar")
        word += "#"
        stack = [0]
        word_index = 0
        while len(stack) > 0:
            word_symbol = word[word_index]
            last_state = stack[-1]
            action = self.table[last_state][word_symbol]
            if action.action == ActionType.ERROR:
                return False
            if action.action == ActionType.ACCEPT:
                return True
            if action.action == ActionType.SHIFT:
                stack.append(word_symbol)
                stack.append(action.value)
                word_index += 1
            if action.action == ActionType.REDUCE:
                rule = self.grammar.rules[action.value]
                for j in range(len(rule.product)):
                    stack.pop()
                    stack.pop()
                s = stack[-1]
                stack.append(rule.non_terminal)
                stack.append(self.transitions[(s, rule.non_terminal)])
        return False

    def print_table(self):
        print(f'{"":>7}', end="")
        for key in self.table[0].keys():
            print(f'{key:>7}', end="")
        print("")
        for i in range(len(self.table)):
            print(f'{str(i):>7}', end="")
            for key, value in self.table[i].items():
                s = ""
                if value.action == ActionType.ACCEPT:
                    s = "A"
                if value.action == ActionType.SHIFT:
                    s = "s(" + str(value.value) + ")"
                if value.action == ActionType.REDUCE:
                    s = "r(" + str(value.value) + ")"
                print(f'{s:>7}', end="")
            print("")

    def print_states(self):
        for i in range(len(self.states)):
            print("________")
            print("State {}".format(i))
            for situation in self.states[i]:
                rule = situation.rule.non_terminal + " -> "
                if situation.position > 0:
                    rule += situation.rule.product[:situation.position]
                rule += "." + situation.rule.product[situation.position:] + ", " + situation.next
                print(rule)
            print("")
            print("Edges: ", end="")
            for key in self.transitions.keys():
                if key[0] == i:
                    print((self.transitions[key], key[1]), end=" ")
            print("")
        print("________")
