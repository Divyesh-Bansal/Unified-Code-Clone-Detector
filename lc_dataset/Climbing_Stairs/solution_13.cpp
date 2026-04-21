#include <vector>
#include <cstring>

class Solution {
    int dp[50];
public:
    int calculate(int n) {
        if (n <= 2) return n;
        if (dp[n] != -1) return dp[n];
        return dp[n] = calculate(n - 1) + calculate(n - 2);
    }
    int climbStairs(int n) {
        std::memset(dp, -1, sizeof(dp));
        return calculate(n);
    }
};
