class Solution {
public:
    int findDuplicate(vector<int>& nums) {
        vector<int> freq(nums.size(), 0);
        for (int num : nums) {
            freq[num]++;
            if (freq[num] > 1) {
                return num;
            }
        }
        return -1;
    }
};