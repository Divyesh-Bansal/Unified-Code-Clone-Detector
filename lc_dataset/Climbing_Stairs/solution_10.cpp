#include <iostream>

class Solution {
public:
    int climbStairs(int n) {
        if (n <= 2) return n;
        int p = 1, q = 2;
        for (int i = 3; i <= n; ++i) {
            int r = p + q;
            p = q;
            q = r;
        }
        return q;
    }
};
