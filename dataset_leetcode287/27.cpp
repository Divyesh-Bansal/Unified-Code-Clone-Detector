class Solution {
public:
    int findDuplicate(vector<int>& arr) {
        int n = arr.size();
        for(int i=0;i<n;i++){
            int temp = abs(arr[i]);
            arr[temp-1] = -arr[temp-1];
            if(arr[temp-1] > 0) return temp;
        }     
        return -1;   
    }
};