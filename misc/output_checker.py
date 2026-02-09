
import os
from typing import List, Tuple, Optional


def _fail(msg: str) -> Tuple[bool, str]:
    return (False, msg)


def _normalize_newlines(s: str) -> str:
    return s.replace("\r\n", "\n").replace("\r", "\n")


def _split_lines_strict(text: str) -> Tuple[Optional[List[str]], Optional[str]]:
    """
    Strict output whitespace handling:
    - Allow either no trailing '\n' or exactly one trailing '\n'.
    - Disallow ending with '\n\n' (extra blank line at EOF).
    - Disallow any empty lines in the middle (checked later).
    """
    t = _normalize_newlines(text)

    if t.endswith("\n\n"):
        return None, "Output has more than one trailing newline (extra blank line at end)"

    if t == "":
        return [], None

    if t.endswith("\n"):
        t = t[:-1]  # drop the single allowed trailing newline

    return t.split("\n"), None


def _check_line_tokens_exact(line: str, expected_tokens: int, line_no: int, case_no: Optional[int] = None) -> Tuple[Optional[List[str]], Optional[str]]:
    """
    Enforce strict tokenization:
    - No leading/trailing spaces.
    - Tokens separated by single spaces only.
    - Exactly expected_tokens tokens.
    Tabs or other whitespace are not accepted.
    """
    prefix = f"Case {case_no}: " if case_no is not None else ""
    if line == "":
        return None, f"{prefix}Line {line_no}: empty line is not allowed"
    if line[0] == " " or line[-1] == " ":
        return None, f"{prefix}Line {line_no}: leading/trailing spaces are not allowed"
    if "\t" in line:
        return None, f"{prefix}Line {line_no}: tabs are not allowed"
    if "  " in line:
        return None, f"{prefix}Line {line_no}: multiple consecutive spaces are not allowed"
    toks = line.split(" ")
    if len(toks) != expected_tokens:
        return None, f"{prefix}Line {line_no}: expected {expected_tokens} tokens, got {len(toks)}"
    return toks, None


def _parse_int(tok: str, ctx: str) -> Tuple[Optional[int], Optional[str]]:
    if tok == "":
        return None, f"{ctx}: empty token"
    # Strict integer format: optional leading '-', then digits. No '+'.
    if tok[0] == "-":
        if len(tok) == 1 or not tok[1:].isdigit():
            return None, f"{ctx}: invalid integer token '{tok}'"
    else:
        if not tok.isdigit():
            return None, f"{ctx}: invalid integer token '{tok}'"
    try:
        return int(tok), None
    except Exception:
        return None, f"{ctx}: could not parse integer '{tok}'"


def _parse_input_cases(input_text: str) -> Tuple[Optional[List[Tuple[int, int, int, List[int]]]], Optional[str]]:
    """
    Supports:
    - Single test case: n M D then n integers
    - Multiple test cases (if present): T then T blocks each: n M D then n integers
    Detection strategy:
    - First try to parse as a single case consuming all tokens.
    - If that fails, try to parse as T cases.
    """
    t = _normalize_newlines(input_text)
    parts = t.split()
    if len(parts) < 3:
        return None, "Input: expected at least 3 integers"

    def parse_one_case_at(idx: int, case_no: Optional[int] = None) -> Tuple[Optional[Tuple[int, int, int, List[int]]], Optional[str], int]:
        # returns (case, err, next_idx)
        if idx + 3 > len(parts):
            return None, "Input: incomplete case header (need n M D)", idx
        n, err = _parse_int(parts[idx], f"Input{'' if case_no is None else f' case {case_no}'} n")
        if err:
            return None, err, idx
        m, err = _parse_int(parts[idx + 1], f"Input{'' if case_no is None else f' case {case_no}'} M")
        if err:
            return None, err, idx
        d, err = _parse_int(parts[idx + 2], f"Input{'' if case_no is None else f' case {case_no}'} D")
        if err:
            return None, err, idx
        assert n is not None and m is not None and d is not None

        if n < 1 or n > 200000:
            return None, f"Input{'' if case_no is None else f' case {case_no}'}: n={n} out of constraints [1..200000]", idx
        if m < 1 or m > 20:
            return None, f"Input{'' if case_no is None else f' case {case_no}'}: M={m} out of constraints [1..20]", idx
        if d < 0 or d > n:
            return None, f"Input{'' if case_no is None else f' case {case_no}'}: D={d} out of constraints [0..n={n}]", idx

        if idx + 3 + n > len(parts):
            return None, f"Input{'' if case_no is None else f' case {case_no}'}: expected {n} array values, got {len(parts) - (idx + 3)}", idx

        a: List[int] = []
        base = idx + 3
        for i in range(n):
            v, err = _parse_int(parts[base + i], f"Input{'' if case_no is None else f' case {case_no}'} a[{i+1}]")
            if err:
                return None, err, idx
            assert v is not None
            if v < -10**9 or v > 10**9:
                return None, f"Input{'' if case_no is None else f' case {case_no}'}: a[{i+1}]={v} out of constraints [-1e9..1e9]", idx
            a.append(v)

        return (n, m, d, a), None, base + n

    # Attempt single-case parse consuming all tokens.
    one, err, next_idx = parse_one_case_at(0)
    if err is None and next_idx == len(parts):
        return [one], None

    # Attempt multi-case parse: T then T cases.
    T, errT = _parse_int(parts[0], "Input T")
    if errT:
        # Return original single-case parse error if T isn't parseable
        return None, err if err is not None else "Input: could not parse as single case or multi-case"
    assert T is not None
    if T < 1:
        return None, f"Input: T={T} is invalid; expected T >= 1"

    cases: List[Tuple[int, int, int, List[int]]] = []
    idx = 1
    for case_no in range(1, T + 1):
        case, errc, idx2 = parse_one_case_at(idx, case_no=case_no)
        if errc:
            return None, errc
        assert case is not None
        cases.append(case)
        idx = idx2

    if idx != len(parts):
        return None, f"Input: extra tokens after reading T={T} cases (extra={len(parts) - idx})"

    return cases, None


def check(input_text: str, output_text: str) -> Tuple[bool, str]:
    cases, err = _parse_input_cases(input_text)
    if err:
        return _fail(err)
    assert cases is not None

    lines, err = _split_lines_strict(output_text)
    if err:
        return _fail(err)
    if lines is None:
        return _fail("Internal error: could not split output")

    if len(lines) == 0:
        return _fail("Output is empty; expected at least one line with 'k S'")

    # Parse output sequentially by cases.
    line_ptr = 0  # 0-based index into lines

    for case_idx, (n, M, D, a) in enumerate(cases, start=1):
        if line_ptr >= len(lines):
            return _fail(f"Case {case_idx}: missing output (expected line with 'k S')")

        # Line: k S
        toks, err = _check_line_tokens_exact(lines[line_ptr], 2, line_ptr + 1, case_no=case_idx)
        if err:
            return _fail(err)
        k, err = _parse_int(toks[0], f"Case {case_idx}, line {line_ptr + 1} k")
        if err:
            return _fail(err)
        S, err = _parse_int(toks[1], f"Case {case_idx}, line {line_ptr + 1} S")
        if err:
            return _fail(err)
        assert k is not None and S is not None
        line_ptr += 1

        # k must be at least 1 (a single-element segment always exists; empty set not specified)
        if k < 1:
            return _fail(f"Case {case_idx}: k={k} is invalid; expected k >= 1")
        if k > n:
            return _fail(f"Case {case_idx}: k={k} is invalid; expected k <= n={n}")

        if line_ptr + k > len(lines):
            return _fail(f"Case {case_idx}: expected {k} segment lines after 'k S', but output ended early")

        # Prefix sums
        pref = [0] * (n + 1)
        for i in range(1, n + 1):
            pref[i] = pref[i - 1] + a[i - 1]

        segs: List[Tuple[int, int]] = []
        for j in range(k):
            cur_line_no = line_ptr + 1  # 1-based global line number
            toks, err = _check_line_tokens_exact(lines[line_ptr], 2, cur_line_no, case_no=case_idx)
            if err:
                return _fail(err)
            l, err = _parse_int(toks[0], f"Case {case_idx}, line {cur_line_no} l")
            if err:
                return _fail(err)
            r, err = _parse_int(toks[1], f"Case {case_idx}, line {cur_line_no} r")
            if err:
                return _fail(err)
            assert l is not None and r is not None

            if l < 1 or l > n:
                return _fail(f"Case {case_idx}, line {cur_line_no}: l={l} out of range [1..n={n}]")
            if r < 1 or r > n:
                return _fail(f"Case {case_idx}, line {cur_line_no}: r={r} out of range [1..n={n}]")
            if l > r:
                return _fail(f"Case {case_idx}, line {cur_line_no}: invalid segment (l={l} > r={r})")
            length = r - l + 1
            if length > M:
                return _fail(f"Case {case_idx}, line {cur_line_no}: segment length {length} exceeds M={M}")

            seg_sum = pref[r] - pref[l - 1]
            if seg_sum != S:
                return _fail(
                    f"Case {case_idx}, line {cur_line_no}: segment sum is {seg_sum}, but declared S is {S}"
                )

            segs.append((l, r))
            line_ptr += 1

        # Check ordering by increasing r, tie by increasing l (i.e., nondecreasing (r,l)).
        for i in range(1, k):
            l1, r1 = segs[i - 1]
            l2, r2 = segs[i]
            if (r2, l2) < (r1, l1):
                return _fail(
                    f"Case {case_idx}: segments not sorted by increasing r then l; "
                    f"segment {i} is (l={l1}, r={r1}), segment {i+1} is (l={l2}, r={r2})"
                )

        # Check no overlap + silence rule on consecutive segments in this order.
        for i in range(1, k):
            l_prev, r_prev = segs[i - 1]
            l_cur, r_cur = segs[i]
            if l_cur <= r_prev:
                return _fail(
                    f"Case {case_idx}: overlap between segment {i} (l={l_prev}, r={r_prev}) and "
                    f"segment {i+1} (l={l_cur}, r={r_cur})"
                )
            if l_cur <= r_prev + D:
                gap = l_cur - r_prev - 1
                return _fail(
                    f"Case {case_idx}: silence rule violated between segment {i} (l={l_prev}, r={r_prev}) and "
                    f"segment {i+1} (l={l_cur}, r={r_cur}); gap={gap}, required >= D={D}"
                )

        # Note: Optimality (max k, min S, lexicographic minimality) cannot be validated without solving.

    if line_ptr != len(lines):
        return _fail(f"Output: extra lines/tokens after last test case (extra_lines={len(lines) - line_ptr})")

    return (True, "OK")


if __name__ == "__main__":
    in_path = os.environ.get("INPUT_PATH")
    out_path = os.environ.get("OUTPUT_PATH")
    if not in_path or not out_path:
        print("False")
    else:
        with open(in_path, "r", encoding="utf-8") as f:
            input_text = f.read()
        with open(out_path, "r", encoding="utf-8") as f:
            output_text = f.read()
        ok, _ = check(input_text, output_text)
        print("True" if ok else "False")
