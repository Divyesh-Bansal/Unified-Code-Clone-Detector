class Solution {
public:
    int findDuplicate(vector<int>& arr) {
        //Slow-Fast Pointer Approach
        int slow = arr[0] , fast = arr[0] ;

        do{
            slow = arr[slow] ;//update by 1 or +1
            fast = arr[arr[fast]] ;//update by 2 or +2
        } while(slow != fast) ;

        //again re-initialize slow with arr[0]
        slow = arr[0] ;
        
        //this slow or fast will meet at repeating value
        while(slow != fast){
            slow = arr[slow] ; //update by 1 or +1
            fast = arr[fast] ; //update by 1 or +1
        }
        return slow ; 
        //here you can return slow or fast anyone
        //both will indicate the same repeating value
    }
};