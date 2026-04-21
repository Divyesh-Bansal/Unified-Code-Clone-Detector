#include <vector>
#include <unordered_map>
using namespace std;
class Solution {
public:
    int singleNumber(vector<int>& input) {
        unordered_map<int, int> m;
        for (int n : input) m[n]++;
        for (auto const& pair : m) {
            if (pair.second == 1) return pair.first;
        }
        return -1;
    }
};
