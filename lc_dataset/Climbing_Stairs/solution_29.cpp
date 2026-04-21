#include <vector>

class Solution {
public:
    int climbStairs(int n) {
        if (n == 1) return 1;
        std::vector<int> computed(n + 1);
        computed[1] = 1;
        computed[2] = 2;
        for (int curr = 3; curr <= n; curr++) {
            computed[curr] = computed[curr - 1] + computed[curr - 2];
        }
        return computed[n];
    }
};
