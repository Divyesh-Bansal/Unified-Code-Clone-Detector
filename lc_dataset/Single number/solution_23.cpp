#include <vector>
#include <algorithm>
using namespace std;
class Solution {
public:
    int singleNumber(vector<int>& input) {
        sort(input.begin(), input.end());
        for (int i = 0; i < (int)input.size() - 1; i += 2) {
            if (input[i] != input[i+1]) return input[i];
        }
        return input.back();
    }
};
