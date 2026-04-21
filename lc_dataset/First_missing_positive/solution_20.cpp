#include <vector>
#include <cmath>
using namespace std;

class Solution {
public:
    int firstMissingPositive(vector<int>& arr) {
        int n = arr.size();
        bool hasOne = false;
        for(int x : arr) if(x == 1) hasOne = true;
        if(!hasOne) return 1;
        for(int i = 0; i < n; i++) {
            if(arr[i] <= 0 || arr[i] > n) arr[i] = 1;
        }
        for(int i = 0; i < n; i++) {
            int val = abs(arr[i]);
            if(val == n) arr[0] = -abs(arr[0]);
            else arr[val] = -abs(arr[val]);
        }
        for(int i = 1; i < n; i++) {
            if(arr[i] > 0) return i;
        }
        return (arr[0] > 0) ? n : n + 1;
    }
};
