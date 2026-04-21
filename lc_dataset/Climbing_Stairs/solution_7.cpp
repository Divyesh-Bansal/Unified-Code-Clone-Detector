#include <iostream>

class Solution {
public:
    int climbStairs(int n) {
        if (n <= 2) return n;
        int curr_ways = 1, next_ways = 2;
        for (int i = 3; i <= n; ++i) {
            int tmp = curr_ways + next_ways;
            curr_ways = next_ways;
            next_ways = tmp;
        }
        return next_ways;
    }
};
