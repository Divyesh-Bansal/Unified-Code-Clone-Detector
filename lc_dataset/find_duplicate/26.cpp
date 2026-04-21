class Solution {
public:
    int findDuplicate(vector<int>& nums) {
        int n=nums.size();
        sort(nums.begin(),nums.end());
        int s=0;
        int e=n-1;
        int mid=s+(e-s)/2;
        int ans;
        while(s<=e){
            if(mid-nums[mid]>=0){
                e=mid-1;
            }
            else {
                ans=nums[mid];
                s=mid+1;
            }
            mid=s+(e-s)/2;

        }
        return ans;        
    }
};