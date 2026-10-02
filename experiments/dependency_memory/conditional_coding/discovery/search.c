/* Bounded exact-population conditional codebook discovery, no model calls. */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include "base.h"

enum { SOURCES=4096, CENTERS=64, BITS=12 };
static uint8_t one[16][16], triple_cost[SOURCES][SOURCES];
static int8_t margins[SOURCES][BITS];
static uint16_t left[CENTERS][CENTERS], right[CENTERS];
static uint16_t right_score[SOURCES][CENTERS];
static uint8_t left_message[SOURCES][CENTERS], left_cost[SOURCES][CENTERS];
static int64_t left_margins[CENTERS][CENTERS][BITS], right_margins[CENTERS][BITS];
static uint32_t random_state;

static uint32_t random_next(void) {
    random_state ^= random_state << 13;
    random_state ^= random_state >> 17;
    random_state ^= random_state << 5;
    return random_state;
}

static void initialize(void) {
    for (int x=0; x<16; ++x)
        for (int a=0; a<16; ++a)
            for (int o=0; o<4; ++o)
                for (int j=0; j<4; ++j)
                    if (j!=o) one[x][a]+=(uint8_t)(((x>>j)&1)!=((a>>o)&1));
    for (int x=0; x<SOURCES; ++x) {
        for (int a=0; a<SOURCES; ++a)
            triple_cost[x][a]=(uint8_t)(one[x&15][a&15]+one[(x>>4)&15][(a>>4)&15]+one[x>>8][a>>8]);
        for (int r=0; r<3; ++r) {
            int word=(x>>(4*r))&15, weight=0;
            for (int j=0; j<4; ++j) weight+=(word>>j)&1;
            for (int o=0; o<4; ++o)
                margins[x][4*r+o]=(int8_t)(3-2*weight+2*((word>>o)&1));
        }
    }
}

static uint16_t modal(uint16_t old, const int64_t delta[BITS]) {
    uint16_t result=old;
    for (int bit=0; bit<BITS; ++bit) {
        if (delta[bit]<0) result|=(uint16_t)(1<<bit);
        if (delta[bit]>0) result&=(uint16_t)~(1<<bit);
        /* A zero margin keeps the old bit, including empty cells. */
    }
    return result;
}

static void print_book(const uint16_t centers[CENTERS]) {
    printf("[");
    for (int i=0; i<CENTERS; ++i) printf("%s%u",i ? "," : "",centers[i]);
    printf("]");
}

static void plain_control(void) {
    uint16_t centers[CENTERS];
    memcpy(centers,BASE,sizeof centers);
    uint64_t previous=UINT64_MAX;
    for (int step=0; step<=8; ++step) {
        int64_t delta[CENTERS][BITS]={{0}};
        uint64_t errors=0;
        for (int x=0; x<SOURCES; ++x) {
            int selected=0;
            uint8_t best=triple_cost[x][centers[0]];
            for (int m=1; m<CENTERS; ++m) {
                uint8_t cost=triple_cost[x][centers[m]];
                if (cost<best) {best=cost; selected=m;}
            }
            errors+=best;
            for (int bit=0; bit<BITS; ++bit) delta[selected][bit]+=margins[x][bit];
        }
        if (errors>previous) {fprintf(stderr,"plain loss increased\n"); exit(2);}
        previous=errors;
        printf("{\"kind\":\"plain\",\"step\":%d,\"errors\":%llu,\"outcomes\":147456,\"book\":",step,(unsigned long long)errors);
        print_book(centers); printf("}\n"); fflush(stdout);
        if (step<8) for (int m=0; m<CENTERS; ++m) centers[m]=modal(centers[m],delta[m]);
    }
}

static uint64_t evaluate(void) {
    memset(left_margins,0,sizeof left_margins);
    memset(right_margins,0,sizeof right_margins);
    for (int y=0; y<SOURCES; ++y)
        for (int b=0; b<CENTERS; ++b)
            right_score[y][b]=(uint16_t)(64*triple_cost[y][right[b]]+b);
    for (int x=0; x<SOURCES; ++x)
        for (int b=0; b<CENTERS; ++b) {
            int selected=0;
            uint8_t best=triple_cost[x][left[b][0]];
            for (int a=1; a<CENTERS; ++a) {
                uint8_t cost=triple_cost[x][left[b][a]];
                if (cost<best) {best=cost; selected=a;}
            }
            left_cost[x][b]=best;
            left_message[x][b]=(uint8_t)selected;
        }
    uint64_t errors=0;
    for (int x=0; x<SOURCES; ++x) {
        uint16_t add[CENTERS];
        uint32_t counts[CENTERS]={0};
        for (int b=0; b<CENTERS; ++b) add[b]=(uint16_t)(64*left_cost[x][b]);
        for (int y=0; y<SOURCES; ++y) {
            uint16_t best=UINT16_MAX;
            for (int b=0; b<CENTERS; ++b) {
                uint16_t value=(uint16_t)(right_score[y][b]+add[b]);
                if (value<best) best=value;
            }
            int selected=best&63;
            errors+=best>>6;
            ++counts[selected];
            for (int bit=0; bit<BITS; ++bit) right_margins[selected][bit]+=margins[y][bit];
        }
        for (int b=0; b<CENTERS; ++b) {
            int a=left_message[x][b];
            for (int bit=0; bit<BITS; ++bit)
                left_margins[b][a][bit]+=(int64_t)counts[b]*margins[x][bit];
        }
    }
    return errors;
}

int main(void) {
    clock_t started=clock();
    initialize();
    plain_control();
    uint64_t best_all=UINT64_MAX;
    int best_seed=-1;
    for (int seed=0; seed<=3; ++seed) {
        random_state=(uint32_t)seed;
        for (int b=0; b<CENTERS; ++b) {
            right[b]=BASE[b];
            for (int a=0; a<CENTERS; ++a) {
                left[b][a]=BASE[a];
                if (seed && (random_next()%8==0)) left[b][a]^=(uint16_t)(1<<(random_next()%12));
            }
        }
        uint64_t previous=UINT64_MAX;
        for (int step=0; step<=8; ++step) {
            uint64_t errors=evaluate();
            if (errors>previous) {fprintf(stderr,"conditional loss increased\n"); return 3;}
            previous=errors;
            if (errors<best_all) {best_all=errors; best_seed=seed;}
            printf("{\"kind\":\"conditional\",\"seed\":%d,\"step\":%d,\"errors\":%llu,\"outcomes\":1207959552}\n",seed,step,(unsigned long long)errors);
            fflush(stdout);
            fprintf(stderr,"seed %d step %d: %llu\n",seed,step,(unsigned long long)errors);
            if (step<8) {
                for (int b=0; b<CENTERS; ++b) {
                    right[b]=modal(right[b],right_margins[b]);
                    for (int a=0; a<CENTERS; ++a) left[b][a]=modal(left[b][a],left_margins[b][a]);
                }
            }
        }
        printf("{\"kind\":\"final\",\"seed\":%d,\"errors\":%llu,\"right\":",seed,(unsigned long long)previous);
        print_book(right); printf(",\"left\":[");
        for (int b=0; b<CENTERS; ++b) {if (b) printf(","); print_book(left[b]);}
        printf("]}\n"); fflush(stdout);
    }
    fprintf(stderr,"best seed %d: %llu; clock seconds %.6f\n",best_seed,(unsigned long long)best_all,(double)(clock()-started)/CLOCKS_PER_SEC);
    return 0;
}
