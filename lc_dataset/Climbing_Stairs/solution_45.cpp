#include <cmath>

class Solution {
public:
    int climbStairs(int n) {
        double const5 = std::sqrt(5);
        double ratio1 = (1 + const5) / 2;
        double ratio2 = (1 - const5) / 2;
        return (int)((std::pow(ratio1, n + 1) - std::pow(ratio2, n + 1)) / const5);
    }
};
