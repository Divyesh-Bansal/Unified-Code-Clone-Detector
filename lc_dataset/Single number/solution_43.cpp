#include <vector>
#include <unordered_set>
using namespace std;
class Solution {
public:
    int singleNumber(vector<int>& input) {
        unordered_set<int> s;
        for (int n : input) {
            if (s.count(n)) s.erase(n);
            else s.insert(n);
        }
        return *s.begin();
    }
};
