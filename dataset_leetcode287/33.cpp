class Solution {
public:
    int findDuplicate(vector<int>& v) {
        int n=v.size();
        int ans=0;
        sort(v.begin(),v.end());
        for(int i=0;i<n;i++){
            int com=v[i];
            int freq=0;
            while(i<n && v[i]==com){
                freq++;
                i++;
            }
            i--;
            if(freq>1){
                ans=com;
            }
        }
        return ans;
    }
};