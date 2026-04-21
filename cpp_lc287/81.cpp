class Solution {
public:
    int findDuplicate(vector<int>& v) {
       sort(v.begin(),v.end());
       int n=v.size();
       int low=0;
       int high=n-1;
       int mid;
       
        while(low <= high){
        mid = (low+high)/2;
         
        if(v[mid] <= mid){
            high = mid-1;
        }
        else{
            low = mid + 1;
        }
    }
       return low;
    }
};