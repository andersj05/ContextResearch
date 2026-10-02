#define main original_screen_main
#include "swap.c"
#undef main

int main(void) {
    if (original_screen_main()!=0) return 1;
    int selected_a=-1, selected_c=-1;
    int64_t global_gain=0;
    for (int a=0; a<64; ++a) {
        int selected=BASE[a];
        int64_t best_gain=0;
        for (int c=0; c<4096; ++c) {
            int64_t gained=0, lost=0;
            for (int v=1; v<37; ++v) gained+=(int64_t)v*negative[c][v];
            for (int t=1; t<37; ++t) lost+=(int64_t)t*penalty_hist[a][c][t];
            int64_t gain=gained-lost;
            if (gain>best_gain) {best_gain=gain; selected=c;}
        }
        printf("{\"kind\":\"half_slot\",\"removed_index\":%d,\"replacement\":%d,\"gain\":%lld}\n",a,selected,(long long)best_gain);
        if (best_gain>global_gain) {global_gain=best_gain; selected_a=a; selected_c=selected;}
    }
    printf("{\"kind\":\"half_selected\",\"removed_index\":%d,\"replacement\":%d,\"gain\":%lld,\"candidate_replacements\":262144}\n",selected_a,selected_c,(long long)global_gain);
    fprintf(stderr,"half best index %d word %d gain %lld\n",selected_a,selected_c,(long long)global_gain);
    return 0;
}
