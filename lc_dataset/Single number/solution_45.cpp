#include <vector>
#include <unordered_set>
using namespace std;
class Solution 
{
public:
    int singleNumber(vector<int>& nums) 
{
        unordered_set<int> elements;
        for (int n : nums) 
{
            if (elements.count(n)) elements.erase(n);
            else elements.insert(n);
        
}
        return *elements.begin();
    
}

};
