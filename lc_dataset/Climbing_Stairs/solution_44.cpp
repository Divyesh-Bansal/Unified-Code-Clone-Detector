#include <cmath>

class Solution {
public:
    int climbStairs(int n) {
        double v_sqrt = std::sqrt(5);
        double v_phi = (1 + v_sqrt) / 2;
        double v_psi = (1 - v_sqrt) / 2;
        return (int)((std::pow(v_phi, n + 1) - std::pow(v_psi, n + 1)) / v_sqrt);
    }
};
