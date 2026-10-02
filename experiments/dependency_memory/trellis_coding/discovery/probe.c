/* Bounded mathematical discovery, not an exhaustive code or model trial. */
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "base.h"

static uint8_t one[16][16];
static uint8_t left[256][256], right[256][256];
static uint32_t random_state;

static uint32_t next_random(void) {
    random_state ^= random_state << 13;
    random_state ^= random_state >> 17;
    random_state ^= random_state << 5;
    return random_state;
}

static void shuffle(int permutation[64], int seed) {
    for (int i=0; i<64; ++i) permutation[i]=i;
    if (!seed) return;
    random_state = (uint32_t)seed;
    for (int i=63; i>0; --i) {
        int j=(int)(next_random()%(uint32_t)(i+1));
        int swap=permutation[i]; permutation[i]=permutation[j]; permutation[j]=swap;
    }
}

static int response(int message, int block, int k, const int permutation[64]) {
    int before=(message>>(2*((block+k-2)%k)))&3;
    int previous=(message>>(2*((block+k-1)%k)))&3;
    int current=(message>>(2*block))&3;
    int phase=block%3;
    int index=phase==0 ? current+4*before+16*previous :
        phase==1 ? previous+4*current+16*before : before+4*previous+16*current;
    return (BASE[permutation[index]]>>(4*phase))&15;
}

static uint64_t score(const int permutation[64], int *distinct) {
    uint16_t book[256];
    uint8_t seen[65536]={0};
    *distinct=0;
    for (int m=0; m<256; ++m) {
        book[m]=0;
        for (int block=0; block<4; ++block)
            book[m] |= (uint16_t)(response(m,block,4,permutation)<<(4*block));
        if (!seen[book[m]]) {seen[book[m]]=1; ++*distinct;}
    }
    for (int x=0; x<256; ++x)
        for (int m=0; m<256; ++m) {
            left[x][m]=one[x&15][book[m]&15]+one[x>>4][(book[m]>>4)&15];
            right[x][m]=one[x&15][(book[m]>>8)&15]+one[x>>4][book[m]>>12];
        }
    uint64_t errors=0;
    for (int high=0; high<256; ++high)
        for (int low=0; low<256; ++low) {
            int best=48;
            for (int m=0; m<256; ++m) {
                int cost=left[low][m]+right[high][m];
                if (cost<best) best=cost;
            }
            errors+=(uint64_t)best;
        }
    return errors;
}

int main(void) {
    for (int x=0; x<16; ++x)
        for (int a=0; a<16; ++a)
            for (int o=0; o<4; ++o)
                for (int j=0; j<4; ++j)
                    if (j!=o) one[x][a]+=(uint8_t)(((x>>j)&1)!=((a>>o)&1));
    int best_seed=-1;
    uint64_t best=UINT64_MAX;
    for (int seed=0; seed<=32; ++seed) {
        int permutation[64], distinct;
        shuffle(permutation,seed);
        uint64_t errors=score(permutation,&distinct);
        if (errors<best) {best=errors; best_seed=seed;}
        printf("{\"seed\":%d,\"errors\":%llu,\"outcomes\":3145728,\"distinct_words\":%d,\"permutation\":[",
               seed,(unsigned long long)errors,distinct);
        for (int i=0; i<64; ++i) printf("%s%d",i ? "," : "",permutation[i]);
        printf("]}\n");
        fflush(stdout);
    }
    fprintf(stderr,"best seed %d: %llu errors (pair-product control 869376)\n",best_seed,(unsigned long long)best);
    return 0;
}
