/* Eight bounded exact conditional single-word swaps of a refined product. */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include "refined.h"

static uint8_t costs[4096][4096], right_cost[4096][64];
static uint16_t centers[64][64];
static uint8_t minimum[4096][64], winner[4096][64], gap[4096][64];
static uint32_t addition[64][4096], penalty[64][64][4096];

static void initialize(void) {
    uint8_t one[16][16]={{0}};
    for (int x=0; x<16; ++x)
        for (int a=0; a<16; ++a)
            for (int o=0; o<4; ++o)
                for (int j=0; j<4; ++j)
                    if (o!=j) one[x][a]+=(uint8_t)(((x>>j)&1)!=((a>>o)&1));
    for (int x=0; x<4096; ++x) {
        for (int c=0; c<4096; ++c)
            costs[x][c]=(uint8_t)(one[x&15][c&15]+one[(x>>4)&15][(c>>4)&15]+one[x>>8][c>>8]);
        for (int b=0; b<64; ++b) right_cost[x][b]=costs[x][BASE[b]];
    }
    for (int b=0; b<64; ++b)
        for (int a=0; a<64; ++a) centers[b][a]=BASE[a];
}

static void left_nearest(void) {
    for (int x=0; x<4096; ++x)
        for (int b=0; b<64; ++b) {
            int first=37, second=37, arg=0;
            for (int a=0; a<64; ++a) {
                int value=costs[x][centers[b][a]];
                if (value<first) {second=first; first=value; arg=a;}
                else if (value<second) second=value;
            }
            minimum[x][b]=(uint8_t)first;
            gap[x][b]=(uint8_t)(second-first);
            winner[x][b]=(uint8_t)arg;
        }
}

static uint64_t screen(void) {
    left_nearest();
    memset(addition,0,sizeof addition);
    memset(penalty,0,sizeof penalty);
    uint64_t errors=0;
    for (int x=0; x<4096; ++x) {
        uint16_t histogram[64][37]={{0}};
        for (int y=0; y<4096; ++y) {
            int first=73, second=73, arg=0;
            for (int b=0; b<64; ++b) {
                int value=minimum[x][b]+right_cost[y][b];
                if (value<first) {second=first; first=value; arg=b;}
                else if (value<second) second=value;
            }
            errors+=first;
            for (int b=0; b<64; ++b) {
                int other=b==arg ? second : first;
                int threshold=other-right_cost[y][b];
                if (threshold<0) threshold=0;
                if (threshold>36) threshold=36;
                ++histogram[b][threshold];
            }
        }
        for (int b=0; b<64; ++b) {
            uint32_t potential[37]={0};
            uint32_t remaining=4096-histogram[b][0];
            for (int t=1; t<=36; ++t) {
                potential[t]=potential[t-1]+remaining;
                remaining-=histogram[b][t];
            }
            int current=minimum[x][b], other=current+gap[x][b], a=winner[x][b];
            uint32_t here=potential[current];
            if (gap[x][b]) {
                for (int c=0; c<4096; ++c) {
                    int candidate=costs[x][c];
                    if (candidate<current) addition[b][c]+=here-potential[candidate];
                    else {
                        int replaced=candidate<other ? candidate : other;
                        penalty[b][a][c]+=potential[replaced]-here;
                    }
                }
            } else {
                for (int c=0; c<4096; ++c)
                    if (costs[x][c]<current) addition[b][c]+=here-potential[costs[x][c]];
            }
        }
    }
    return errors;
}

static uint64_t score_only(void) {
    left_nearest();
    uint64_t errors=0;
    for (int x=0; x<4096; ++x)
        for (int y=0; y<4096; ++y) {
            uint8_t best=73;
            for (int b=0; b<64; ++b) {
                uint8_t value=(uint8_t)(minimum[x][b]+right_cost[y][b]);
                if (value<best) best=value;
            }
            errors+=best;
        }
    return errors;
}

int main(void) {
    clock_t started=clock();
    initialize();
    uint64_t expected=UINT64_MAX, current=0;
    int accepted=0, zero_screen=0;
    for (int step=0; step<8; ++step) {
        current=screen();
        if (expected!=UINT64_MAX && current!=expected) {fprintf(stderr,"predicted gain failed\n"); return 2;}
        int selected_hole=-1, selected_word=-1;
        int64_t global_gain=0;
        printf("{\"kind\":\"screen\",\"step\":%d,\"errors\":%llu,\"candidate_replacements\":16777216,\"best_by_slot\":[",step,(unsigned long long)current);
        for (int b=0; b<64; ++b) {
            for (int a=0; a<64; ++a) {
                int chosen=centers[b][a];
                int64_t best_gain=0;
                for (int c=0; c<4096; ++c) {
                    int64_t gain=(int64_t)addition[b][c]-penalty[b][a][c];
                    if (gain>best_gain) {best_gain=gain; chosen=c;}
                }
                int hole=a+64*b;
                printf("%s[%d,%lld]",hole ? "," : "",chosen,(long long)best_gain);
                if (best_gain>global_gain) {global_gain=best_gain; selected_hole=hole; selected_word=chosen;}
            }
        }
        printf("],\"selected_hole\":%d,\"selected_word\":%d,\"gain\":%lld}\n",selected_hole,selected_word,(long long)global_gain);
        fflush(stdout);
        fprintf(stderr,"step %d: %llu, gain %lld\n",step,(unsigned long long)current,(long long)global_gain);
        if (!global_gain) {zero_screen=1; break;}
        centers[selected_hole>>6][selected_hole&63]=(uint16_t)selected_word;
        expected=current-(uint64_t)global_gain;
        ++accepted;
    }
    current=score_only();
    if (expected!=UINT64_MAX && current!=expected) {fprintf(stderr,"final gain failed\n"); return 3;}
    printf("{\"kind\":\"final\",\"errors\":%llu,\"outcomes\":1207959552,\"accepted\":%d,\"zero_screen\":%s,\"overrides\":[",(unsigned long long)current,accepted,zero_screen ? "true" : "false");
    int printed=0;
    for (int b=0; b<64; ++b)
        for (int a=0; a<64; ++a)
            if (centers[b][a]!=BASE[a]) {
                printf("%s[%d,%u]",printed++ ? "," : "",a+64*b,centers[b][a]);
            }
    printf("]}\n");
    fprintf(stderr,"clock seconds %.6f\n",(double)(clock()-started)/CLOCKS_PER_SEC);
    return 0;
}
