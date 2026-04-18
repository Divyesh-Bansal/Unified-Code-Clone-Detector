class Solution {
public:
    bool check(int mid, vector<int>& nums){
        int count = 0;
        for (int x: nums){
            if (x <= mid) count++;
        }

        return mid < count;
    }
    
    int findDuplicate(vector<int>& nums) {
        int low = 1, high = ssize(nums) - 1;
        int ans = 0;

        while (low <= high){
            int mid = low + (high - low) / 2;

            if (check(mid, nums)){
                ans = mid;
                high = mid - 1;
            }
            else low = mid + 1;
        }

        return ans;
    }
};