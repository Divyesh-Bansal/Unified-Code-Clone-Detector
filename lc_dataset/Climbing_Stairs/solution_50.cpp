#include <cmath>

class Solution {
public:
    int climbStairs(int n) {
        double val5 = std::sqrt(5);
        double u = (1 + val5) / 2;
        double v = (1 - val5) / 2;
        return (int)((std::pow(u, n + 1) - std::pow(v, n + 1)) / val5);
    }
};
