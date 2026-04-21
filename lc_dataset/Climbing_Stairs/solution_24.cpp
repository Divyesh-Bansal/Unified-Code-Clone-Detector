#include <vector>

class Solution {
public:
    int climbStairs(int n) {
        if (n == 1) return 1;
        std::vector<int> arr(n + 1);
        arr[1] = 1;
        arr[2] = 2;
        for (int idx = 3; idx <= n; idx++) {
            arr[idx] = arr[idx - 1] + arr[idx - 2];
        }
        return arr[n];
    }
};
