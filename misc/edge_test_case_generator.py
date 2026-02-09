
def make_case(n, M, D, arr):
    assert len(arr) == n
    return f"{n} {M} {D}\n" + " ".join(map(str, arr))

cases = []

# 1) Minimum n, trivial
cases.append(make_case(1, 1, 0, [5]))

# 2) Minimum n with D = n (forces k=1 anyway)
cases.append(make_case(1, 1, 1, [-7]))

# 3) M > n (cap length), increasing array
cases.append(make_case(5, 20, 0, [1, 2, 3, 4, 5]))

# 4) D >= n (forces at most one chant); mixed signs (min S tie logic for k=1)
cases.append(make_case(6, 3, 6, [-5, 2, -1, 3, -4, 1]))

# 5) Silence-rule boundary D=1, M=1, all equal (requires exact gaps)
cases.append(make_case(7, 1, 1, [0, 0, 0, 0, 0, 0, 0]))

# 6) D=0 adjacency allowed, M=1, all equal => can take all indices
cases.append(make_case(6, 1, 0, [0, 0, 0, 0, 0, 0]))

# 7) All zeros, larger M and D=2 (many optimal packings; tie-breaking/reconstruction)
cases.append(make_case(30, 20, 2, [0] * 30))

# 8) Alternating signs (many repeated sums due to cancellation)
cases.append(make_case(10, 3, 0, [1, -1] * 5))

# 9) Overflow stress for 32-bit prefix sums: large values, n>20, M=20, D=n
cases.append(make_case(50, 20, 50, [10**9] * 50))

# 10) Many duplicate sums; multiple ways to form sum 0 with different lengths
cases.append(make_case(8, 4, 0, [5, 0, 0, -5, 0, 0, 5, -5]))

# 11) Tie-breaking on S with same max k (k=2 possible for S=0 and S=-1; must pick S=-1)
cases.append(make_case(6, 1, 2, [0, -1, 7, 0, -1, 8]))

# 12) Lex tie-break (same k and S, first chant ends at same r with different l => choose smaller l)
# Constructed so max k=2 and only S=5 achieves k=2.
cases.append(make_case(9, 5, 1, [11, -11, 2, 2, 1, 100, 5, 200, -300]))

# 13) Must consider segments of length exactly M (M=3) to achieve max k=2
cases.append(make_case(8, 3, 0, [1000, 2000, -2001, 1234567, 7654321, 3000, -1000, -1001]))

# 14) Max n stress, all zeros (maximum repeated-sum density), D=0
n14, M14, D14 = 200000, 20, 0
zeros_line_14 = ("0 " * (n14 - 1)) + "0"
cases.append(f"{n14} {M14} {D14}\n{zeros_line_14}")

# 15) Max n stress with nontrivial D, alternating pattern (many sum collisions), D=5
n15, M15, D15 = 200000, 20, 5
alt_line_15 = ("1 -1 " * (n15 // 2)).strip()  # n15 is even
cases.append(f"{n15} {M15} {D15}\n{alt_line_15}")

print("Test Cases:")
for i, tc in enumerate(cases, 1):
    print(f"Input {i}:")
    print(tc)
    if i != len(cases):
        print()
