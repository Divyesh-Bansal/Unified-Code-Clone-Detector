#include <vector>
#include <cstring>

class Solution {
    int results[50];
public:
    int getSteps(int n) {
        if (n <= 2) return n;
        if (results[n] != -1) return results[n];
        return results[n] = getSteps(n - 1) + getSteps(n - 2);
    }
    int climbStairs(int n) {
        std::memset(results, -1, sizeof(results));
        return getSteps(n);
    }
};
