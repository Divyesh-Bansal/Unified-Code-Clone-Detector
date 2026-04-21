class Solution {
public:
    int findDuplicate(vector<int>& nums) {
        
        
// for(int i=0;i<nums.size();i++){
//     for(int j=0;j<nums.size();j++){
//         if((nums[i] ^ nums [j]) == 0 && i!=j){
//             return nums[i];


//         }
//     }
// }
//       return -1;   // BRUTE FORCE 








        //using stl -map - BETTER 
//         unordered_map<int,int>mpp;
//         for(int i=0;i<nums.size();i++){
//             mpp[nums[i]]++;

//         }
//         for(auto it:mpp){
//             if(it.second>1){
//                 return it.first;
//             }
//         }
//         return -1;
    
// //TC=O(2n) and SC = O(n)

 //AS THE ABOVE SOLUTION TAKES O(n) SPACE  so 
 //using the FLOYD CYCLE DETECTION HARE AND TORTOISE ALGORITHM
 //SINCE THE DUPLICATE NUMBER CREATE THE CYCLE 
 //Treating as linked list

 //OPTIMIZED
 int tortoise=nums[0];
 int hare=nums[0];

    tortoise = nums[tortoise];
    hare = nums[nums[hare]];
 while(tortoise != hare){
     tortoise = nums[tortoise];
    hare = nums[nums[hare]];

 }
tortoise=nums[0];
while(tortoise != hare){
tortoise=nums[tortoise];
hare=nums[hare];
}
return tortoise;






    }
};