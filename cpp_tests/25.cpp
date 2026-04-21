class Solution {
public:
    int findDuplicate(vector<int>& nums) {
        int n= nums.size();
        int lo = 1;
        int hi = n-1;
        while(lo < hi){
            int mid = (lo + hi)/2;
            int count = 0;
            for(int i=0; i<n; i++){
                if(nums[i] <= mid) count++;
            }
            if(count > mid) hi = mid;
            else lo = mid + 1;
        }
        return lo ;


    }
};