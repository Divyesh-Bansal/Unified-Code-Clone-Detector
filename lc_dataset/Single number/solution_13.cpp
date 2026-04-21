#include <vector>
#include <numeric>
#include <functional>
using namespace std;
class Solution {
public:
    int singleNumber(vector<int>& input) {
        return accumulate(input.begin(), input.end(), 0, bit_xor<int>());
    }
};
