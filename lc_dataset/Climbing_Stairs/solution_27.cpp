#include <vector>

class Solution {
public:
    int climbStairs(int n) {
        if (n == 1) return 1;
        std::vector<int> count(n + 1);
        count[1] = 1;
        count[2] = 2;
        for (int step_idx = 3; step_idx <= n; step_idx++) {
            count[step_idx] = count[step_idx - 1] + count[step_idx - 2];
        }
        return count[n];
    }
};
