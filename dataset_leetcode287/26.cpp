class Solution {
public:
    int findDuplicate(vector<int>& nums) {
        int n=nums.size()-1;
        for(int i=0;i<=n;i++){
            int k=nums[i];
            nums[k%(n+2)]+=(n+2);
        }
        int ans=-1;
        for(int i=0;i<=n;i++){
            if(nums[i]/(n+2)>=2){
                ans=i;
                break;
            }
        }
        return ans;
    }
};