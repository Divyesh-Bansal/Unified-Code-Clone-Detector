#include <vector>

class Solution {
public:
    int climbStairs(int n) {
        if (n == 1) return 1;
        std::vector<int> steps(n + 1);
        steps[1] = 1;
        steps[2] = 2;
        for (int k = 3; k <= n; k++) {
            steps[k] = steps[k - 1] + steps[k - 2];
        }
        return steps[n];
    }
};
