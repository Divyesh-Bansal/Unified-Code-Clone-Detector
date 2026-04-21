#pragma GCC optimize("O3", "unroll-loops")
class Solution {
public:
//Bit manipulation! compare sum of i & sum of nums[i] at each bit
    static int findDuplicate(vector<int>& nums) {
        int n=nums.size()-1, duplicate=0;
        int B=31-__builtin_clz(n);//only bit 0~bit B used
        for(int b=0; b<=B; b++){
            int sum_i=0, sum_x=0;
            for(int i=0; i<=n; i++){
                sum_i+=(((i>>b)&1)>0);
                sum_x+=(((nums[i]>>b)&1)>0);
            }
            if (sum_x>sum_i)//<=> duplicate has at b-th bit set 
                duplicate|=(1<<b);
        }
        return duplicate;
    }
};