class Solution {
public:
    int findDuplicate(vector<int>& nums) {
        for(int i:nums){
            int j=abs(i);
            if(nums[j]<0)
                return j;
            nums[j]=-nums[j];
        }
        return -1;
    }
};