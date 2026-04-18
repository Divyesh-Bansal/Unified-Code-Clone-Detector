class Solution {
    public int findDuplicate(int[] nums) {
        int mod = (int)1e5 + 1;
        for(int i=0;i<nums.length;i++) {
            int ind = Math.abs(nums[i])%mod;
            if(nums[ind]/mod > 0) {
                return ind;
            }
            nums[ind] += mod;
        }
        return -1;
    }
}