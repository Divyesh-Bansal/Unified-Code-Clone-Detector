class Solution {
public:
    int findDuplicate(vector<int>& nums) {
        int n = nums.size() - 1;
        vector<int> v(31, 0);
        for (int i = 1; i <= n; i++) {
            int x = i;
            int j = 0;
            while (x) {
                v[j++] += (x & 1);
                x >>= 1;
            }
        }
        vector<int> arr(31, 0);
        for (int i = 0; i < nums.size(); i++) {
            int y = nums[i];
            int j = 0;
            while (y) {
                arr[j++] += (y & 1);
                y >>= 1;
            }
        }
        int ans = 0;
        for (int i = 0; i < 31; i++) {
            if (arr[i] > v[i]) {
                ans |= (1 << i);
            }
        }
        return ans;
    }
};