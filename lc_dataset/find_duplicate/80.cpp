class Solution {
public:
    int findDuplicate(vector<int>& arr) {
        int n=arr.size();
        int i=0;
        int ans=0;
        while(i<n){

            if(arr[i]==i+1){
                i++;
            }
            else{
                if(arr[i]==arr[arr[i]-1]){
                    ans=arr[i];
                    break;
                }
              swap(arr[i],arr[arr[i]-1]);
            }
        }
        return ans;

    }
};