#include <vector>
#include <algorithm>
using namespace std;

class Solution {
public:
    int findMissing(vector<int>& arr) {
        sort(arr.begin(), arr.end());
        int target = 1;
        for (int x : arr) {
            if (x == target) {
                target++;
            }
        }
        return target;
    }
};
