"""
This module parses Mana Costs
"""
import itertools
import re
from typing import Dict, Iterable, List, Sequence, Set, Tuple

from shared.pd_exception import ParseException

START = ''
DIGIT = '[0-9]'
COLOR = '[WURBGCS]'
X = '[XYZ]'
SLASH = '/'
MODIFIER = 'P'
HALF = 'H'
HYBRID = 'SPECIAL-HYBRID'

def parse(s: str) -> List[str]:
    tmp = ''
    tokens = []
    mode = START
    stripped = s.replace('{', '').replace('}', '')
    for c in list(stripped):
        if mode == START:
            if re.match(DIGIT, c):
                tmp += c
                mode = DIGIT
            elif re.match(COLOR, c):
                tmp += c
                mode = COLOR
            elif re.match(X, c):
                tokens.append(c)
                tmp = ''
                mode = START
            elif re.match(HALF, c):
                tmp += c
                mode = HALF
            else:
                raise InvalidManaCostException('Symbol must start with {digit} or {color} or {x} or {half}, `{c}` found in `{s}`.'.format(digit=DIGIT, color=COLOR, x=X, half=HALF, c=c, s=s))
        elif mode == DIGIT:
            if re.match(DIGIT, c):
                tmp += c
            elif re.match(COLOR, c) or re.match(X, c):
                tokens.append(tmp)
                tmp = c
                mode = COLOR
            elif re.match(SLASH, c):
                tmp += c
                mode = SLASH
            else:
                raise InvalidManaCostException('Digit must be followed by {digit}, {color} or {slash}, `{c}` found in `{s}`.'.format(digit=DIGIT, color=COLOR, slash=SLASH, c=c, s=s))
        elif mode == COLOR:
            if re.match(COLOR, c):
                tokens.append(tmp)
                tmp = c
                mode = COLOR
            elif re.match(SLASH, c):
                tmp += c
                mode = SLASH
            else:
                raise InvalidManaCostException('Color must be followed by {color} or {slash}, `{c}` found in `{s}`.'.format(color=COLOR, slash=SLASH, c=c, s=s))
        elif mode == SLASH:
            if re.match(MODIFIER, c):
                tokens.append(tmp + c)
                tmp = ''
                mode = START
            elif re.match(COLOR, c):
                tmp += c
                mode = HYBRID
            else:
                raise InvalidManaCostException('Slash must be followed by {color} or {modifier}, `{c}` found in `{s}`.'.format(color=COLOR, modifier=MODIFIER, c=c, s=s))
        elif mode == HALF:
            if re.match(COLOR, c):
                tokens.append(tmp + c)
                tmp = ''
                mode = START
            else:
                raise InvalidManaCostException('H must be followed by {color}, `{c}` found in `{s}`.'.format(color=COLOR, c=c, s=s))
        elif mode == HYBRID:  # Having an additional check after HYBRID for a second slash accomodates hybrid phyrexian mana like Tamiyo, Compleated Sage
            if re.match(SLASH, c):
                tmp += c
                mode = SLASH
            elif re.match(DIGIT, c):
                tokens.append(tmp)
                tmp = c
                mode = DIGIT
            elif re.match(COLOR, c):
                tokens.append(tmp)
                tmp = c
                mode = COLOR
            elif re.match(X, c):
                tokens.append(tmp)
                tokens.append(c)
                tmp = ''
                mode = START
            elif re.match(HALF, c):
                tokens.append(tmp)
                tmp = c
                mode = HALF
            else:
                raise InvalidManaCostException('Hybrid must be followed by {slash} or {digit} or {color} or {x} or {half}, `{c}` found in `{s}`.'.format(slash=SLASH, digit=DIGIT, color=COLOR, x=X, half=HALF, c=c, s=s))
    if tmp:
        tokens.append(tmp)
    return tokens

def colors(symbols: List[str]) -> Dict[str, Set[str]]:
    return colors_from_colored_symbols(colored_symbols(symbols))

def colors_from_colored_symbols(all_colored_symbols: Dict[str, List[str]]) -> Dict[str, Set[str]]:
    return {'required': set(all_colored_symbols['required']), 'also': set(all_colored_symbols['also'])}

def colored_symbols(symbols: List[str]) -> Dict[str, List[str]]:
    cs: Dict[str, List[str]] = {'required': [], 'also': []}
    for symbol in symbols:
        if generic(symbol) or variable(symbol):
            pass
        elif hybrid(symbol):
            parts = symbol.split(SLASH)
            cs['also'].append(parts[0])
            cs['also'].append(parts[1])
        elif phyrexian(symbol):
            cs['also'].append(symbol[0])
        elif twobrid(symbol):
            parts = symbol.split(SLASH)
            cs['also'].append(parts[1])
        elif colored(symbol):
            cs['required'].append(symbol)
        else:
            raise InvalidManaCostException('Unrecognized symbol type: `{symbol}` in `{symbols}`'.format(symbol=symbol, symbols=symbols))
    return cs

def cmc(mana_cost: str) -> float:
    symbols = parse(mana_cost)
    total = 0.0
    for symbol in symbols:
        if generic(symbol):
            total += int(symbol)
        elif twobrid(symbol):
            total += 2.0
        elif half(symbol):
            total += 0.5
        elif variable(symbol):
            total += 0.0
        elif phyrexian(symbol) or hybrid(symbol) or colored(symbol):
            total += 1.0
        else:
            raise InvalidManaCostException(f"Can't calculate CMC - I don't recognize '{symbol}'")
    return total

def generic(symbol: str) -> bool:
    return bool(re.match('^{digit}+$'.format(digit=DIGIT), symbol))

def variable(symbol: str) -> bool:
    return bool(re.match('^{x}$'.format(x=X), symbol))

def phyrexian(symbol: str) -> bool:
    return bool(re.match('^({color}/)?{color}/{modifier}$'.format(color=COLOR, modifier=MODIFIER), symbol))

def hybrid(symbol: str) -> bool:
    return bool(re.match('^{color}/{color}(/{modifier})?$'.format(color=COLOR, modifier=MODIFIER), symbol))

def twobrid(symbol: str) -> bool:
    return bool(re.match('^2/{color}$'.format(color=COLOR), symbol))

def half(symbol: str) -> bool:
    return bool(re.match('^{half}{color}$'.format(half=HALF, color=COLOR), symbol))

def colored(symbol: str) -> bool:
    return bool(re.match('^{color}$'.format(color=COLOR), symbol))

def has_x(mana_cost: str) -> bool:
    return len([symbol for symbol in parse(mana_cost) if variable(symbol)]) > 0

def order(symbols: Iterable[str]) -> List[str]:
    permutations = itertools.permutations(symbols)
    return list(sorted(permutations, key=order_score)[0])

def order_score(initial_symbols: Tuple[str, ...]) -> int:
    symbols = [symbol for symbol in initial_symbols if symbol not in ('C', 'S')]
    if not symbols:
        return 0
    score = 0
    positions = ['W', 'U', 'B', 'R', 'G']
    current = positions.index(symbols[0])
    for symbol in symbols[1:]:
        position = positions.index(symbol)
        distance = position - current
        if position < current:
            distance += len(positions)
        score += distance
        current = position
    return score * 10 + positions.index(symbols[0])

# Gives an integer sort ordering for a set of colors already in min(order_score) ordering.
# Use on unsorted lists of color symbols will produce undesirable results.
def sort_score(symbols: Sequence[str]) -> int:
    positions = [None, 'C', 'S', 'W', 'U', 'B', 'R', 'G']
    score = 0
    for i, symbol in enumerate(reversed(symbols), start=1):
        score += positions.index(symbol) * 10 * i
    return score

class InvalidManaCostException(ParseException):
    pass
