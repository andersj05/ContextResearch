/* Exact one-slot conditional replacement screen; source/decoder law fixed. */
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <time.h>
#include "refined.h"

static uint8_t cost[4096][4096], best[4096], delta[4096], arg[4096];
static uint16_t negative[4096][37], penalty_hist[64][4096][37];
static uint32_t near_gain[64][37], removal_factor[64][37], addition[64][4096];

int main(void) {
    clock_t started=clock();
    uint8_t one[16][16]={{0}};
    for (int x=0; x<16; ++x)
        for (int a=0; a<16; ++a)
            for (int o=0; o<4; ++o)
                for (int j=0; j<4; ++j)
                    if (o!=j) one[x][a]+=(uint8_t)(((x>>j)&1)!=((a>>o)&1));
    int max_delta=0, max_negative=0;
    uint64_t half_errors=0;
    for (int x=0; x<4096; ++x) {
        for (int c=0; c<4096; ++c)
            cost[x][c]=(uint8_t)(one[x&15][c&15]+one[(x>>4)&15][(c>>4)&15]+one[x>>8][c>>8]);
        best[x]=37; arg[x]=0;
        for (int a=0; a<64; ++a)
            if (cost[x][BASE[a]]<best[x]) {best[x]=cost[x][BASE[a]]; arg[x]=(uint8_t)a;}
        int second=37;
        for (int a=0; a<64; ++a)
            if (a!=arg[x] && cost[x][BASE[a]]<second) second=cost[x][BASE[a]];
        delta[x]=(uint8_t)(second-best[x]);
        if (delta[x]>max_delta) max_delta=delta[x];
        half_errors+=best[x];
        for (int c=0; c<4096; ++c) {
            int d=(int)cost[x][c]-best[x];
            if (d<0) {++negative[c][-d]; if (-d>max_negative) max_negative=-d;}
            if (delta[x]) {
                int t=d>0 ? d : 0;
                if (t>delta[x]) t=delta[x];
                ++penalty_hist[arg[x]][c][t];
            }
        }
    }
    for (int b=0; b<64; ++b) {
        for (int y=0; y<4096; ++y) {
            int e=(int)cost[y][BASE[b]]-best[y];
            for (int v=1; v<=max_negative; ++v)
                if (v>e) near_gain[b][v]+=(uint32_t)(v-e);
            if (arg[y]==b && delta[y])
                for (int t=1; t<=max_delta; ++t)
                    removal_factor[b][t]+=(uint32_t)(t<delta[y] ? t : delta[y]);
        }
        for (int c=0; c<4096; ++c)
            for (int v=1; v<=max_negative; ++v)
                addition[b][c]+=(uint32_t)negative[c][v]*near_gain[b][v];
    }
    uint64_t baseline=half_errors*8192;
    printf("{\"kind\":\"setup\",\"half_errors\":%llu,\"baseline_errors\":%llu,\"max_unique_margin\":%d,\"max_candidate_gain_margin\":%d,\"candidates\":16777216}\n",(unsigned long long)half_errors,(unsigned long long)baseline,max_delta,max_negative);
    int selected_hole=-1, selected_word=-1;
    int64_t selected_gain=0;
    uint32_t selected_addition=0, selected_penalty=0;
    for (int b=0; b<64; ++b) {
        for (int a=0; a<64; ++a) {
            int chosen=BASE[a];
            int64_t best_gain=0;
            uint32_t gained=0, lost=0;
            for (int c=0; c<4096; ++c) {
                uint32_t penalty=0;
                for (int t=1; t<=max_delta; ++t)
                    penalty+=(uint32_t)penalty_hist[a][c][t]*removal_factor[b][t];
                int64_t gain=(int64_t)addition[b][c]-penalty;
                if (gain>best_gain) {best_gain=gain; chosen=c; gained=addition[b][c]; lost=penalty;}
            }
            int hole=a+64*b;
            printf("{\"kind\":\"slot\",\"hole\":%d,\"replacement\":%d,\"gain\":%lld,\"addition_gain\":%u,\"removal_penalty\":%u}\n",hole,chosen,(long long)best_gain,gained,lost);
            if (best_gain>selected_gain) {
                selected_gain=best_gain; selected_hole=hole; selected_word=chosen;
                selected_addition=gained; selected_penalty=lost;
            }
        }
    }
    if (selected_hole>=0) {
        int a=selected_hole&63, b=selected_hole>>6;
        uint64_t direct=0;
        for (int y=0; y<4096; ++y)
            for (int x=0; x<4096; ++x) {
                int dx=arg[x]==a ? delta[x] : 0;
                int dy=arg[y]==b ? delta[y] : 0;
                int old=best[x]+best[y]+(dx<dy ? dx : dy);
                int added=cost[x][selected_word]+cost[y][BASE[b]];
                direct+=(uint64_t)(old<added ? old : added);
            }
        if (direct!=baseline-(uint64_t)selected_gain) {fprintf(stderr,"histogram/direct mismatch\n"); return 2;}
        printf("{\"kind\":\"selected\",\"hole\":%d,\"replacement\":%d,\"gain\":%lld,\"addition_gain\":%u,\"removal_penalty\":%u,\"errors\":%llu,\"outcomes\":1207959552,\"full_source_pairs_checked\":16777216}\n",selected_hole,selected_word,(long long)selected_gain,selected_addition,selected_penalty,(unsigned long long)direct);
    } else printf("{\"kind\":\"selected\",\"positive_gain\":false}\n");
    fprintf(stderr,"selected hole %d, word %d, gain %lld; clock seconds %.6f\n",selected_hole,selected_word,(long long)selected_gain,(double)(clock()-started)/CLOCKS_PER_SEC);
    return 0;
}
