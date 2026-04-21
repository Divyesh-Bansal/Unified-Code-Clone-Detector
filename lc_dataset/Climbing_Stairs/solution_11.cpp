#include <vector>
#include <cstring>

class Solution {
    int memo[50];
public:
    int helper(int n) {
        if (n <= 2) return n;
        if (memo[n] != -1) return memo[n];
        return memo[n] = helper(n - 1) + helper(n - 2);
    }
    int climbStairs(int n) {
        std::memset(memo, -1, sizeof(memo));
        return helper(n);
    }
};
