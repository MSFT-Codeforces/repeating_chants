
def fmt_case(n, M, D, arr):
    return f"{n} {M} {D}\n" + " ".join(map(str, arr))

cases = []

# 1) Minimum n, D=0
cases.append((1, 1, 0, [5]))

# 2) Minimum n, D=n (forces at most one chant)
cases.append((1, 1, 1, [-7]))

# 3) M > n, all zeros (many equal-sum segments)
cases.append((5, 20, 0, [0, 0, 0, 0, 0]))

# 4) Alternating signs, D=0
cases.append((6, 3, 0, [1, -1, 1, -1, 1, -1]))

# 5) Alternating with zeros, D=1 (gap constraint active)
cases.append((6, 3, 1, [2, -2, 0, 2, -2, 0]))

# 6) Strictly increasing, small M
cases.append((7, 2, 0, [1, 2, 3, 4, 5, 6, 7]))

# 7) Strictly decreasing negatives, small M
cases.append((7, 2, 0, [-1, -2, -3, -4, -5, -6, -7]))

# 8) D very large (almost n), only one chant possible
cases.append((8, 3, 7, [3, -1, 4, -2, 5, -3, 6, -4]))

# 9) M=1 (only singletons), duplicates & negatives
cases.append((10, 1, 0, [0, 0, 0, 1, 1, -1, -1, 2, -2, 2]))

# 10) Silence rule off-by-one target: need exact l2 = r1 + D + 1
cases.append((8, 2, 2, [0, 0, 0, 0, 0, 0, 0, 0]))

# 11) D=0 adjacency allowed (ensure not accidentally enforcing a gap)
cases.append((5, 2, 0, [0, 0, 0, 0, 0]))

# 12) Lex tie-breaking among same k and S (singles vs pairs), must compare by (r,l)
cases.append((6, 2, 1, [1, 0, 1, 0, 1, 0]))

# 13) Same maximum k but different S; must minimize S
cases.append((4, 1, 1, [-1, 0, -1, 0]))

# 14) Large magnitude values to force 64-bit sums
cases.append((5, 5, 0, [1000000000, 1000000000, 1000000000, 1000000000, -1000000000]))

# 15) Overlapping-rich equal sums: greedy long segment would reduce k; must maximize k
cases.append((7, 4, 0, [2, -2, 2, -2, 2, -2, 2]))

print("Test Cases: ")
for i, (n, M, D, arr) in enumerate(cases, 1):
    print(f"Input {i}:")
    print(fmt_case(n, M, D, arr))
    if i != len(cases):
        print()
