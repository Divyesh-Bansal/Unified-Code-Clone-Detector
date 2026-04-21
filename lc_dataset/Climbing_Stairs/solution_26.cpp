#include <vector>

class Solution {
public:
    int climbStairs(int n) {
        if (n == 1) return 1;
        std::vector<int> ways(n + 1);
        ways[1] = 1;
        ways[2] = 2;
        for (int n_steps = 3; n_steps <= n; n_steps++) {
            ways[n_steps] = ways[n_steps - 1] + ways[n_steps - 2];
        }
        return ways[n];
    }
};
