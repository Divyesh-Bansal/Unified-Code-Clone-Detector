class Solution {
public:
    int findDuplicate(vector<int>& nums) {
        int n = nums.size();
        int idx = nums[0];
        while(true) {
            int tmp = nums[idx];
            if(tmp==0) return idx;
            nums[idx] = 0;
            idx = tmp;
        }
    }
};