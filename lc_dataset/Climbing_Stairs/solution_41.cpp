#include <cmath>

class Solution {
public:
    int climbStairs(int n) {
        double sqrt5 = std::sqrt(5);
        double phi = (1 + sqrt5) / 2;
        double psi = (1 - sqrt5) / 2;
        return (int)((std::pow(phi, n + 1) - std::pow(psi, n + 1)) / sqrt5);
    }
};
