#include <iostream>

class Solution {
public:
    int climbStairs(int n) {
        if (n <= 2) return n;
        int v1 = 1, v2 = 2;
        for (int i = 3; i <= n; ++i) {
            int v3 = v1 + v2;
            v1 = v2;
            v2 = v3;
        }
        return v2;
    }
};
