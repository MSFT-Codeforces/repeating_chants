#include <algorithm>
#include <iostream>
#include <utility>
#include <vector>

using namespace std;

struct Segment {
    long long sum;
    int l;
    int r;
};

static bool segmentSort(const Segment &a, const Segment &b) {
    if (a.sum != b.sum) return a.sum < b.sum;
    if (a.r != b.r) return a.r < b.r;
    return a.l < b.l;
}

static bool chantKeyLess(const pair<int, int> &a, const pair<int, int> &b) {
    // Keys are (r, l)
    if (a.first != b.first) return a.first < b.first;
    return a.second < b.second;
}

static bool lexKeysLess(const vector<pair<int, int>> &a, const vector<pair<int, int>> &b) {
    // Standard lexicographic compare on (r,l) pairs
    size_t n = min(a.size(), b.size());
    for (size_t i = 0; i < n; i++) {
        if (a[i] == b[i]) continue;
        return chantKeyLess(a[i], b[i]);
    }
    return a.size() < b.size();
}

static vector<int> buildIndexSequence(int endIdx, const vector<int> &pred) {
    vector<int> seq;
    int cur = endIdx;
    while (cur != -1) {
        seq.push_back(cur);
        cur = pred[cur];
    }
    reverse(seq.begin(), seq.end());
    return seq;
}

static vector<pair<int, int>> buildKeySequenceFromEnd(int endIdx,
                                                      const vector<pair<int, int>> &segs,
                                                      const vector<int> &pred) {
    // segs stores (l,r). Keys are (r,l) in chain order.
    vector<int> idxSeq = buildIndexSequence(endIdx, pred);
    vector<pair<int, int>> keys;
    keys.reserve(idxSeq.size());
    for (int idx : idxSeq) {
        int l = segs[idx].first;
        int r = segs[idx].second;
        keys.push_back({r, l});
    }
    return keys;
}

static bool chainEndLexLess(int endA,
                            int endB,
                            const vector<pair<int, int>> &segs,
                            const vector<int> &pred) {
    // Compare two chains (ending at endA vs endB) by lex order of (r,l) sequences.
    if (endB == -1) return true;   // any valid chain is better than "none"
    if (endA == -1) return false;

    vector<pair<int, int>> keysA = buildKeySequenceFromEnd(endA, segs, pred);
    vector<pair<int, int>> keysB = buildKeySequenceFromEnd(endB, segs, pred);
    return lexKeysLess(keysA, keysB);
}

int main() {
    ios::sync_with_stdio(false);
    cin.tie(nullptr);

    int n, M, D;
    cin >> n >> M >> D;
    vector<long long> a(n + 1);
    for (int i = 1; i <= n; i++) {
        cin >> a[i];
    }

    // Enumerate all segments with length <= M (brute force).
    vector<Segment> segments;
    long long reserveCount = 1LL * n * min(M, n);
    if (reserveCount > 0) {
        segments.reserve(static_cast<size_t>(reserveCount));
    }

    for (int l = 1; l <= n; l++) {
        long long sum = 0;
        for (int len = 1; len <= M && l + len - 1 <= n; len++) {
            int r = l + len - 1;
            sum += a[r];
            segments.push_back({sum, l, r});
        }
    }

    if (segments.empty()) {
        // Should not happen under constraints (n>=1, M>=1).
        cout << 0 << " " << 0 << "\n";
        return 0;
    }

    sort(segments.begin(), segments.end(), segmentSort);

    int bestGlobalK = -1;
    long long bestGlobalS = 0;
    vector<pair<int, int>> bestGlobalKeys;   // (r,l) keys for lex compare
    vector<pair<int, int>> bestGlobalChants; // (l,r) to print

    // Process each group of equal sums.
    size_t i = 0;
    while (i < segments.size()) {
        size_t j = i;
        while (j < segments.size() && segments[j].sum == segments[i].sum) {
            j++;
        }

        long long curSum = segments[i].sum;

        // Build list of chants (l,r) for this sum, sorted by (r,l) already.
        vector<pair<int, int>> segs;
        segs.reserve(j - i);
        for (size_t t = i; t < j; t++) {
            segs.push_back({segments[t].l, segments[t].r});
        }

        int m = static_cast<int>(segs.size());
        vector<int> dpLen(m, 1);
        vector<int> pred(m, -1);

        // Quadratic DP per sum group: maximize count, tie-break by lex smallest chain (r,l).
        for (int x = 0; x < m; x++) {
            for (int y = 0; y < x; y++) {
                // Compatibility: l_x > r_y + D
                long long lx = segs[x].first;
                long long ry = segs[y].second;
                if (lx > ry + static_cast<long long>(D)) {
                    int candLen = dpLen[y] + 1;
                    if (candLen > dpLen[x]) {
                        dpLen[x] = candLen;
                        pred[x] = y;
                    } else if (candLen == dpLen[x]) {
                        // Both candidates give same length; choose lex smaller chain ending at predecessor.
                        if (chainEndLexLess(y, pred[x], segs, pred)) {
                            pred[x] = y;
                        }
                    }
                }
            }
        }

        // Choose the best chain for this sum: max length, then lex smallest (r,l).
        int bestEnd = 0;
        for (int x = 1; x < m; x++) {
            if (dpLen[x] > dpLen[bestEnd]) {
                bestEnd = x;
            } else if (dpLen[x] == dpLen[bestEnd]) {
                if (chainEndLexLess(x, bestEnd, segs, pred)) {
                    bestEnd = x;
                }
            }
        }

        int curK = dpLen[bestEnd];
        vector<int> idxSeq = buildIndexSequence(bestEnd, pred);

        vector<pair<int, int>> curKeys;
        vector<pair<int, int>> curChants;
        curKeys.reserve(idxSeq.size());
        curChants.reserve(idxSeq.size());

        for (int idx : idxSeq) {
            int l = segs[idx].first;
            int r = segs[idx].second;
            curKeys.push_back({r, l});
            curChants.push_back({l, r});
        }

        // Compare with global best: maximize k, minimize S, then lex smallest (r,l) sequence.
        bool take = false;
        if (curK > bestGlobalK) {
            take = true;
        } else if (curK == bestGlobalK) {
            if (curSum < bestGlobalS) {
                take = true;
            } else if (curSum == bestGlobalS) {
                if (bestGlobalKeys.empty() || lexKeysLess(curKeys, bestGlobalKeys)) {
                    take = true;
                }
            }
        }

        if (take) {
            bestGlobalK = curK;
            bestGlobalS = curSum;
            bestGlobalKeys = curKeys;
            bestGlobalChants = curChants;
        }

        i = j;
    }

    cout << bestGlobalK << " " << bestGlobalS << "\n";
    for (const auto &p : bestGlobalChants) {
        cout << p.first << " " << p.second << "\n";
    }

    return 0;
}