#define main original_screen_main
#include "swap.c"
#undef main

static int rebuild(const uint16_t centers[64], uint64_t *errors) {
    memset(negative,0,sizeof negative);
    memset(penalty_hist,0,sizeof penalty_hist);
    int max_delta=0;
    *errors=0;
    for (int x=0; x<4096; ++x) {
        best[x]=37; arg[x]=0;
        for (int a=0; a<64; ++a)
            if (cost[x][centers[a]]<best[x]) {best[x]=cost[x][centers[a]]; arg[x]=(uint8_t)a;}
        int second=37;
        for (int a=0; a<64; ++a)
            if (a!=arg[x] && cost[x][centers[a]]<second) second=cost[x][centers[a]];
        delta[x]=(uint8_t)(second-best[x]);
        if (delta[x]>max_delta) max_delta=delta[x];
        *errors+=best[x];
        for (int c=0; c<4096; ++c) {
            int d=(int)cost[x][c]-best[x];
            if (d<0) ++negative[c][-d];
            if (delta[x]) {
                int t=d>0 ? d : 0;
                if (t>delta[x]) t=delta[x];
                ++penalty_hist[arg[x]][c][t];
            }
        }
    }
    return max_delta;
}

int main(void) {
    if (original_screen_main()!=0) return 1;
    uint16_t centers[64];
    memcpy(centers,BASE,sizeof centers);
    int accepted=0, zero_screen=0;
    uint64_t errors=0;
    for (int step=0; step<=16; ++step) {
        int max_delta=rebuild(centers,&errors);
        uint32_t gained[4096]={0};
        for (int c=0; c<4096; ++c)
            for (int v=1; v<37; ++v) gained[c]+=(uint32_t)v*negative[c][v];
        int chosen_a=-1, chosen_c=-1;
        int64_t gain=0;
        for (int a=0; a<64; ++a) {
            for (int c=0; c<4096; ++c) {
                uint32_t lost=0;
                for (int t=1; t<=max_delta; ++t) lost+=(uint32_t)t*penalty_hist[a][c][t];
                int64_t improvement=(int64_t)gained[c]-lost;
                if (improvement>gain) {gain=improvement; chosen_a=a; chosen_c=c;}
            }
        }
        printf("{\"kind\":\"refine\",\"step\":%d,\"errors\":%llu,\"removed_index\":%d,\"replacement\":%d,\"gain\":%lld,\"screened_candidates\":262144}\n",step,(unsigned long long)errors,chosen_a,chosen_c,(long long)gain);
        fprintf(stderr,"refine step %d: %llu, gain %lld\n",step,(unsigned long long)errors,(long long)gain);
        if (!gain) {zero_screen=1; break;}
        if (step==16) break;
        centers[chosen_a]=(uint16_t)chosen_c;
        ++accepted;
    }
    printf("{\"kind\":\"refined_final\",\"errors\":%llu,\"accepted\":%d,\"one_swap_zero_screen\":%s,\"book\":[",(unsigned long long)errors,accepted,zero_screen ? "true" : "false");
    for (int a=0; a<64; ++a) printf("%s%u",a ? "," : "",centers[a]);
    printf("]}\n");
    return 0;
}
