class Solution {
public:
    int findDuplicate(vector<int>& nums) {
        int first = nums[0];
        int second = nums[0];
        do {
            first = nums[first];
            second = nums[nums[second]];
        } while (first != second);
        
        second = nums[0];
        while (first != second) {
            first = nums[first];
            second = nums[second];
        }
        
        return first; 
    }
};