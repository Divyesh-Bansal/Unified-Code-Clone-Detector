#include <cmath>

class Solution {
public:
    int climbStairs(int n) {
        double r5 = std::sqrt(5);
        double a1 = (1 + r5) / 2;
        double a2 = (1 - r5) / 2;
        return (int)((std::pow(a1, n + 1) - std::pow(a2, n + 1)) / r5);
    }
};
