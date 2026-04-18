public class Solution {
    public int FindDuplicate(int[] nums) {
        int n=nums.Length,result=0;
        bool[] seen=new bool[n+1];
        foreach(int num in nums){
            if(seen[num]){
                return num;
            }
            seen[num]=true;
        }
        return -1;
    }
}