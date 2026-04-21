#include <vector>
#include <cstring>

class Solution {
    int arr[50];
public:
    int ways(int n) {
        if (n <= 2) return n;
        if (arr[n] != -1) return arr[n];
        return arr[n] = ways(n - 1) + ways(n - 2);
    }
    int climbStairs(int n) {
        std::memset(arr, -1, sizeof(arr));
        return ways(n);
    }
};
