
def solve():
    n, M, D = map(int, input().split())
    a = list(map(int, input().split()))
    
    from collections import defaultdict
    by_sum = defaultdict(list)
    
    # Generate all chants grouped by sum
    for l in range(n):
        s = 0
        for r in range(l, min(l + M, n)):
            s += a[r]
            by_sum[s].append((r, l))
    
    best_k = 0
    best_s = float('inf')
    best_selection = []
    
    for s in by_sum:
        # Sort intervals by (r, l)
        intervals = sorted(by_sum[s])
        
        # Greedy selection
        selection = []
        for r, l in intervals:
            if not selection or selection[-1][0] + D < l:
                selection.append((r, l))
        
        k = len(selection)
        
        # Update best according to priorities
        if k > best_k or (k == best_k and s < best_s) or (k == best_k and s == best_s and selection < best_selection):
            best_k = k
            best_s = s
            best_selection = selection
    
    print(best_k, best_s)
    for r, l in best_selection:
        print(l + 1, r + 1)  # Convert to 1-indexed

solve()
