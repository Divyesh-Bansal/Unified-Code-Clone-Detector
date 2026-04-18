
class Solution {
    public int findDuplicate(int[] nums) {
        int slowpointer = nums[0];
        int fastpointer = nums[0];

        do
        {
            slowpointer = nums[slowpointer];
            fastpointer = nums[nums[fastpointer]];


        }while(slowpointer!= fastpointer);

        slowpointer = nums[0];
        while(slowpointer != fastpointer)
        {
            slowpointer = nums[slowpointer];
            fastpointer = nums[fastpointer];
        }


        return slowpointer;
    }
}