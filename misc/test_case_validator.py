
import sys

def is_int_token(tok: str) -> bool:
    if not tok:
        return False
    if tok[0] == '-':
        return len(tok) > 1 and tok[1:].isdigit()
    return tok.isdigit()

def parse_int(tok: str) -> int:
    if not is_int_token(tok):
        raise ValueError("not int token")
    return int(tok)

def bad_line_format(line: str) -> bool:
    # Strict formatting: no empty line, no leading/trailing spaces, no tabs, no double spaces
    if line == "":
        return True
    if line[0] == ' ' or line[-1] == ' ':
        return True
    if '\t' in line or '\v' in line or '\f' in line:
        return True
    if '  ' in line:
        return True
    return False

def split_strict_spaces(line: str):
    # Assumes bad_line_format(line) is False
    parts = line.split(' ')
    # With our format checks, there should be no empty tokens
    if any(p == "" for p in parts):
        raise ValueError("empty token due to spacing")
    return parts

def validate_case(header_line: str, array_line: str) -> bool:
    if bad_line_format(header_line) or bad_line_format(array_line):
        return False

    try:
        h = split_strict_spaces(header_line)
        if len(h) != 3:
            return False
        n = parse_int(h[0])
        M = parse_int(h[1])
        D = parse_int(h[2])
    except Exception:
        return False

    if not (1 <= n <= 200000):
        return False
    if not (1 <= M <= 20):
        return False
    if not (0 <= D <= n):
        return False

    try:
        arr = split_strict_spaces(array_line)
        if len(arr) != n:
            return False
        for tok in arr:
            x = parse_int(tok)
            if x < -10**9 or x > 10**9:
                return False
    except Exception:
        return False

    return True

def validate() -> bool:
    lines = sys.stdin.read().splitlines()

    if not lines:
        return False
    # Disallow blank lines anywhere
    if any(ln == "" for ln in lines):
        return False

    # Optional support for a leading T (not in statement, but allowed for multi-case files).
    # If first line has exactly 1 integer token, interpret as T.
    idx = 0
    first = lines[0]
    if bad_line_format(first):
        return False

    try:
        first_tokens = split_strict_spaces(first)
    except Exception:
        return False

    if len(first_tokens) == 1 and is_int_token(first_tokens[0]):
        try:
            T = parse_int(first_tokens[0])
        except Exception:
            return False
        if T < 1:
            return False
        idx = 1
        if len(lines) != 1 + 2 * T:
            return False
        for _ in range(T):
            if idx + 1 >= len(lines):
                return False
            if not validate_case(lines[idx], lines[idx + 1]):
                return False
            idx += 2
        return True

    # Otherwise, treat input as concatenated testcases, each exactly 2 lines, until EOF.
    if len(lines) % 2 != 0:
        return False
    for i in range(0, len(lines), 2):
        if not validate_case(lines[i], lines[i + 1]):
            return False
    return True

if __name__ == "__main__":
    sys.stdout.write("True" if validate() else "False")
