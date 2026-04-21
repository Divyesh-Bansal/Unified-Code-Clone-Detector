class Solution {
public:
    int findDuplicate(vector<int>& v) {
        int n=v.size();
        int ans=0;
        unordered_map<int,int>cnt;
        for(int i=0;i<n;i++){
            cnt[v[i]]++;
        }
        for(int i=0;i<n+5;i++){
            if(cnt[i]>1){
                ans=i;
            }
        }
        return ans;
    }
};