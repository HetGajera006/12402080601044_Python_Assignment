import math
import re
import sys

class CalculatorError(Exception):
    pass

class InvalidFormatError(CalculatorError):
    pass

class UnknownVariableError(CalculatorError):
    pass

class DivisionByZeroError(CalculatorError):
    pass

class UnsupportedOperatorError(CalculatorError):
    pass
NUMBER = '[+-]?(?:\\d+\\.?\\d*|\\.\\d+)(?:[eE][+-]?\\d+)?'
IDENT = '[A-Za-z_]\\w*'
OPERAND = f'(?:{NUMBER}|{IDENT})'
FORMULA = re.compile(f'^\\s*({OPERAND})\\s*([^\\s\\w.]+)\\s*({OPERAND})\\s*$')
SINGLE = re.compile(f'^\\s*({OPERAND})\\s*$')
ASSIGN = re.compile(f'^\\s*({IDENT})\\s*=\\s*(.+?)\\s*$')
NUM_ONLY = re.compile(NUMBER)
OPERATORS = ('+', '-', '*', '/', '%')

def resolve(token, variables):
    if NUM_ONLY.fullmatch(token):
        return float(token)
    if token in variables:
        return variables[token]
    raise UnknownVariableError(f"variable '{token}' is not defined")

def compute(a, op, b):
    if op not in OPERATORS:
        raise UnsupportedOperatorError(f"operator '{op}' is not supported")
    assert isinstance(a, float) and isinstance(b, float), 'operands must be floats'
    if op in ('/', '%') and b == 0:
        raise DivisionByZeroError('division by zero')
    return {'+': a + b, '-': a - b, '*': a * b, '/': a / b if b else 0.0, '%': a % b if b else 0.0}[op]

def evaluate(expr, variables):
    m = FORMULA.match(expr)
    if m:
        a = resolve(m.group(1), variables)
        b = resolve(m.group(3), variables)
        return compute(a, m.group(2), b)
    m = SINGLE.match(expr)
    if m:
        return resolve(m.group(1), variables)
    raise InvalidFormatError(f"expected 'operand operator operand', got '{expr}'")

def show(value):
    if math.isfinite(value) and value == int(value) and (abs(value) < 1000000000000000.0):
        return str(int(value))
    return repr(value)

def process_line(line, variables):
    m = ASSIGN.match(line)
    if m:
        variables[m.group(1)] = evaluate(m.group(2), variables)
        return None
    return show(evaluate(line, variables))

def main():
    variables = {}
    for raw in sys.stdin:
        line = raw.strip()
        if line.lower() == 'quit':
            break
        if not line:
            continue
        try:
            result = process_line(line, variables)
            if result is not None:
                print(result)
        except CalculatorError as exc:
            print(f'{type(exc).__name__}: {exc}')
if __name__ == '__main__':
    main()
