from typing import List
from collections import deque
from copy import deepcopy
from consts import end_line


class Rule:
    def __init__(self, left: str, right: str):
        self.non_terminal = left
        self.product = right

    def __lt__(self, other):
        if not isinstance(other, Rule):
            return False
        return (self.non_terminal, self.product) < \
               (other.non_terminal, other.product)

    def __eq__(self, other):
        if not isinstance(other, Rule):
            return False
        return (self.non_terminal, self.product) == \
               (other.non_terminal, other.product)

    def __hash__(self):
        return hash((self.non_terminal, self.product))


class Situation:
    def __init__(self, rule: Rule, position=0, symbol=end_line):
        self.rule = rule
        self.position = position
        self.next = symbol

    def __lt__(self, other):
        if not isinstance(other, Situation):
            return False
        return (self.rule, self.position, self.next) < (other.rule, other.position, other.next)

    def __eq__(self, other):
        if not isinstance(other, Situation):
            return False
        return (self.rule, self.position, self.next) == (other.rule, other.position, other.next)

    def __hash__(self):
        return hash((self.rule, self.next))

    def get_scan_symbol(self):
        if self.position >= len(self.rule.product):
            return None
        return self.rule.product[self.position]

    def scan_letter(self):
        if self.position >= len(self.rule.product):
            return None
        new_rule = Rule(self.rule.non_terminal, self.rule.product)
        new_situation = Situation(new_rule, self.position + 1, self.next)
        return new_situation

    def get_rest_word(self):
        if self.position >= len(self.rule.product) - 1:
            return ""
        return self.rule.product[self.position + 1:]


class Grammar:
    def __init__(self, terminals: List[str], non_terminals: List[str], start_symbol: str, rules: List[Rule]):
        self.terminals = terminals
        self.non_terminals = non_terminals
        self.start_symbol = start_symbol
        self.rules = rules
        self.symbols = terminals + non_terminals

    def get_rules_by_symbol(self, symbol):
        if symbol is None:
            return []
        new_rules = []
        for rule in self.rules:
            if rule.non_terminal == symbol:
                new_rules.append(rule)
        return new_rules

    def get_index(self, rule):
        if rule not in self.rules:
            return None
        return self.rules.index(rule)

    def is_terminal(self, symbol):
        return symbol in self.terminals

    def get_first(self):
        """
        Return which terms started words generated from non-terms
        Build oriented graph:
        Vertices - non-terminals, Edges (A -> B) if is rule [A -> XY...B...]
        where all terminals before B must produce epsilon (and may be smth else)
        """
        graph = {symbol: set() for symbol in self.non_terminals}
        terminals = deepcopy(graph)
        first = deepcopy(graph)
        epsilon = self.get_epsilon()
        for rule in self.rules:
            if len(rule.product) == 0:
                continue
            for symbol in rule.product:
                if symbol in self.terminals:
                    terminals[rule.non_terminal].add(symbol)
                    break
                graph[rule.non_terminal].add(symbol)
                if not epsilon[symbol]:
                    break

        for non_term in self.non_terminals:
            visited = set()
            queue = deque()
            queue.append(non_term)
            while len(queue) > 0:
                current = queue.popleft()
                visited.add(current)
                first[non_term] |= terminals[current]
                for next_non_term in graph[current]:
                    if next_non_term not in visited:
                        queue.append(next_non_term)

        for non_term in self.non_terminals:
            if epsilon[non_term]:
                first[non_term].add(end_line)
        return first

    def get_epsilon(self):
        """
        Find non_terms that produce epsilon/empty words
        Updating epsilons while we can
        """
        is_epsilon = {symbol: False for symbol in self.non_terminals}
        for rule in self.rules:
            if len(rule.product) == 0:
                is_epsilon[rule.non_terminal] = True

        changed = True
        while changed:
            changed = False
            for rule in self.rules:
                if is_epsilon[rule.non_terminal]:
                    continue
                is_all_epsilon = True
                for non_term in rule.product:
                    if non_term in self.terminals or not is_epsilon[non_term]:
                        is_all_epsilon = False
                        break
                if is_all_epsilon:
                    is_epsilon[rule.non_terminal] = True
                    changed = True
        return is_epsilon
