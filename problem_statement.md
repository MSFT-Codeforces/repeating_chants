**Repeating Chants**

Time Limit: **32 seconds**

Memory Limit: **256 MB**

You are given an array of $n$ integers $a[1],a[2],\dots,a[n]$ (values may be negative). A **chant** is a contiguous segment $(l,r)$ such that $1 \le l \le r \le n$ and its length is at most $M$, i.e. $r-l+1 \le M$.

A set of chants is **acceptable** if:

1. **No overlap:** no two chosen chants share an index.
2. **Silence rule:** between any two consecutive chosen chants there are at least $D$ untouched stones. Formally, for two chosen chants $(l_1,r_1)$ and $(l_2,r_2)$ with $r_1 < l_2$, it must hold that
   $$l_2 - r_1 - 1 \ge D \quad \text{(equivalently } l_2 > r_1 + D\text{)}.$$
3. **Same resonance:** all chosen chants have the same sum
   $$S = \sum_{i=l}^{r} a[i].$$

Among all acceptable sets, choose the unique one according to the following priorities:

1. Maximize the number of chants $k$.
2. Among those, minimize the common sum $S$.
3. Among those, sort the chosen chants by increasing $r$ (and for equal $r$, increasing $l$). Let this ordered list be
   $$(r_1,l_1),(r_2,l_2),\dots,(r_k,l_k).$$
   Choose the solution with the lexicographically smallest such sequence.

You must output the chosen chants in the required order (increasing $r$, tie by increasing $l$).

**Input Format:-**

- The first line contains three integers $n$, $M$, $D$.
- The second line contains $n$ integers $a[1],a[2],\dots,a[n]$.

**Output Format:-**

- Print two integers $k$ and $S$.
- Then print $k$ lines, each containing two integers $l$ and $r$ describing a chosen chant, in increasing order of $r$ (and for equal $r$, increasing $l$).

**Constraints:-**

- $1 \le n \le 200000$
- $1 \le M \le 20$
- $0 \le D \le n$
- $-10^9 \le a[i] \le 10^9$
**Examples:-**
 - **Input:**
```
5 5 0
1000000000 1000000000 1000000000 1000000000 -1000000000
```

 - **Output:**
```
4 1000000000
1 1
2 2
3 3
4 4
```

 - **Input:**
```
7 4 0
2 -2 2 -2 2 -2 2
```

 - **Output:**
```
4 2
1 1
3 3
5 5
7 7
```

**Note:-**

In the first example, since $D=0$ we may place chants back-to-back as long as they do not overlap, and $M=5$ does not restrict any segment here. Taking the four single-element chants $(1,1),(2,2),(3,3),(4,4)$ gives the common sum
$$S=a[1]=a[2]=a[3]=a[4]=10^9,$$
so $k=4$. Any chant including index $5$ would have sum $-10^9$ (for length $1$) or would change the sum away from $10^9$, so it cannot be added while keeping the same resonance.

In the first example, the chosen chants are printed in increasing order of $r$ (and for equal $r$, increasing $l$), which here is simply $(1,1),(2,2),(3,3),(4,4)$.

In the second example, the array alternates $2,-2,2,-2,\dots$ and $D=0$, so choosing every positive element as a length-$1$ chant yields four non-overlapping chants:
$$(1,1),(3,3),(5,5),(7,7),$$
each with sum $S=2$, hence $k=4$. Longer segments of length at most $M=4$ can also sum to $2$ (for example $[1,3]$), but using longer segments would reduce the maximum possible number of non-overlapping chants, so the optimal solution keeps single-element chants.