class Solution {
public:
    int findDuplicate(vector<int>& nums) {
        sort(nums.begin(),nums.end());
        int start=0;
        int end=nums.size()-1;
        int mid=start+(end-start)/2;
        while(start<=end)
        {
            mid=start+(end-start)/2;
            if ((mid > 0 && nums[mid] == nums[mid - 1]) ||
                                                            (mid < nums.size() - 1 && nums[mid] == nums[mid + 1]))
            {
             return nums[mid];
            }
            if(nums[mid]<=mid)
            {
                end=mid-1;
            }
            if(nums[mid]>mid)
            {
                start=mid+1;
            }
        }
        return nums[mid];
    }
};