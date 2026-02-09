
import sys
import random

CHUNK = 20000  # chunk size for streaming numbers without large peak memory


def write_array(n, value_at_index):
    """
    Writes n integers separated by spaces, in a single (very long) line.
    value_at_index: function i -> int for 0-based index i
    """
    w = sys.stdout.write
    first = True
    for start in range(0, n, CHUNK):
        end = min(n, start + CHUNK)
        chunk = [str(value_at_index(i)) for i in range(start, end)]
        s = " ".join(chunk)
        if first:
            w(s)
            first = False
        else:
            w(" " + s)
    w("\n")


def emit_case(idx, n, M, D, value_at_index):
    sys.stdout.write(f"Input {idx}:\n")
    sys.stdout.write(f"{n} {M} {D}\n")
    write_array(n, value_at_index)


def main():
    sys.stdout.write("Test Cases: \n")

    n = 200000
    rng = random.Random(123456)

    # 1) All zeros, max density of equal sums; D=0 adjacency allowed; M=20 max
    emit_case(1, n, 20, 0, lambda i: 0)
    sys.stdout.write("\n")

    # 2) All zeros but strong silence rule near M (forces careful gap handling)
    emit_case(2, n, 20, 19, lambda i: 0)
    sys.stdout.write("\n")

    # 3) Off-by-one stress for D=1, M=1 (should allow exactly one untouched stone between)
    emit_case(3, n, 1, 1, lambda i: 0)
    sys.stdout.write("\n")

    # 4) D=0, M=1 (should allow taking adjacent singletons; catches accidental +1 gap)
    emit_case(4, n, 1, 0, lambda i: 0)
    sys.stdout.write("\n")

    # 5) Overflow stress: all 1e9, sums up to 2e10 for length 20
    emit_case(5, n, 20, 0, lambda i: 10**9)
    sys.stdout.write("\n")

    # 6) Alternating extremes: many segments sum to 0; huge cancellation; D=0
    emit_case(6, n, 20, 0, lambda i: 10**9 if (i % 2 == 0) else -10**9)
    sys.stdout.write("\n")

    # 7) Alternating small: tons of equal-sum segments (especially 0), but with nontrivial D
    emit_case(7, n, 20, 5, lambda i: 1 if (i % 2 == 0) else -1)
    sys.stdout.write("\n")

    # 8) Strictly increasing: many distinct-ish sums; prefix sums reach ~2e10 => needs 64-bit
    emit_case(8, n, 20, 0, lambda i: i + 1)
    sys.stdout.write("\n")

    # 9) Random wide range with D=n (forces k=1; tests selecting minimal S among all segments)
    # Use rng to keep determinism.
    def val9(_i, _rng=rng):
        return _rng.randint(-10**9, 10**9)
    emit_case(9, n, 20, n, val9)
    sys.stdout.write("\n")

    # 10) Sparse spikes among zeros: many identical sums + tricky overlaps; heavy hash collisions
    # Pattern: mostly 0, with +1e9 every 50 positions, -1e9 every 50 positions offset by 25
    def val10(i):
        if i % 50 == 0:
            return 10**9
        if i % 50 == 25:
            return -10**9
        return 0
    emit_case(10, n, 20, 0, val10)


if __name__ == "__main__":
    main()
