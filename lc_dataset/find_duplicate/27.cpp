class Solution {
public:
    int findDuplicate(vector<int>& nums) {
        int i = 0;

        while(i < nums.size()) {
            int &x = nums[i];

            if(x == i) {
                i++;
            }
            else if(x != nums[x]) {
                swap(x, nums[x]);
            }
            else {
                return x;
            }
        }

        return 0;
    }
};