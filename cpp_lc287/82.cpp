class Solution {
public:
    int findDuplicate(vector<int>& v) {
       sort(v.begin(),v.end());
       int n=v.size();
       int low=0;
       int high=n-1;
       int mid;
       
       while(low<high){
         mid=(high+low)/2;
         if(mid==0){
           if(v[mid]==v[mid+1]){
               return v[mid];
           }
           else{
               low=mid+1;
           }
         }
         else if(mid==n-1){
            if(v[mid]==v[mid-1]){
               return v[mid];
           }
           else{
               high=mid-1;
           }
         }
         else{
             if(v[mid]==v[mid+1] || v[mid]==v[mid-1]){
                 return v[mid];
               }
            else{
             if(v[mid]<=mid){
                 high=mid-1;
             }
             else{
                 low=mid+1;
             }
         }
         } 
       }
    return 0;
    }
};