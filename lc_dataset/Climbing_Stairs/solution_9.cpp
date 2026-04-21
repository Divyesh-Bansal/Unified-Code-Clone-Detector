#include <iostream>

class Solution {
public:
    int climbStairs(int n) {
        if (n <= 2) return n;
        int first_step = 1, second_step = 2;
        for (int i = 3; i <= n; ++i) {
            int sum = first_step + second_step;
            first_step = second_step;
            second_step = sum;
        }
        return second_step;
    }
};
