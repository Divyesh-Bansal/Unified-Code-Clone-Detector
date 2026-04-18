class Solution {
public:
    int findDuplicate(vector<int>& nums) {
        int arr[100002] ={0};
    
        for(int i = 0 ; i < nums.size() ; i++){
            //incrementing numbers count
            arr[nums[i]]++;
            //checking if number alredy exists
            if(arr[nums[i]] > 1){
                return nums[i];
            }
            
        }
        return -1;
    }
};