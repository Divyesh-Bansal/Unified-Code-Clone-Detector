#include <cmath>

class Solution {
public:
    int climbStairs(int n) {
        double s5 = std::sqrt(5);
        double p = (1 + s5) / 2;
        double q = (1 - s5) / 2;
        return (int)((std::pow(p, n + 1) - std::pow(q, n + 1)) / s5);
    }
};
