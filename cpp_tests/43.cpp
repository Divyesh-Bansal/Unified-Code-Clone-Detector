class Solution {
private:
    int validNums(vector<int> &nums, int mid){

        int cnt = 0;

        for(const int &num :nums){
            if(num <= mid)
                cnt++;
        }

        return cnt;

    }


public:
    int findDuplicate(vector<int>& nums) {
        int m = nums.size();
        int st = 1, end = m-1;

        while(st<end){
            int mid = st + (end-st)/2;

            int count = validNums(nums,mid);

            if(count>mid)
                end = mid;

            else
                st = mid+1;
        }

        return st;
    }
};