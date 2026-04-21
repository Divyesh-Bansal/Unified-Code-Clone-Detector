#include <vector>
using namespace std;
class Solution {
public:
    int singleNumber(vector<int>& input) {
        int result = 0;
        for (int x : input) {
            result ^= x;
        }
        return result;
    }
};
