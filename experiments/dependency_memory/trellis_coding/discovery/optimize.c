/* Post-hoc, bounded exact four-block table search. No model calls. */
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <time.h>
#include "base.h"
#include "seed.h"

static uint8_t one[16][16], labels[3][64], words[256][4];
static uint8_t costs[256][65536], baseline[65536], work[65536];

static int index_for(int message, int block) {
    int before=(message>>(2*((block+2)%4)))&3;
    int previous=(message>>(2*((block+3)%4)))&3;
    int current=(message>>(2*block))&3;
    switch (block%3) {
        case 0: return current+4*before+16*previous;
        case 1: return previous+4*current+16*before;
        default: return before+4*previous+16*current;
    }
}

static uint64_t population_score(void) {
    memset(work,48,sizeof work);
    for (int message=0; message<256; ++message)
        for (int x=0; x<65536; ++x)
            if (costs[message][x]<work[x]) work[x]=costs[message][x];
    uint64_t total=0;
    for (int x=0; x<65536; ++x) total+=work[x];
    return total;
}

int main(void) {
    clock_t started=clock();
    for (int x=0; x<16; ++x)
        for (int a=0; a<16; ++a)
            for (int o=0; o<4; ++o)
                for (int j=0; j<4; ++j)
                    if (j!=o) one[x][a]+=(uint8_t)(((x>>j)&1)!=((a>>o)&1));
    for (int phase=0; phase<3; ++phase)
        for (int index=0; index<64; ++index)
            labels[phase][index]=(BASE[PERM[index]]>>(4*phase))&15;
    for (int message=0; message<256; ++message) {
        for (int block=0; block<4; ++block)
            words[message][block]=labels[block%3][index_for(message,block)];
        for (int x=0; x<65536; ++x)
            for (int block=0; block<4; ++block)
                costs[message][x]+=one[(x>>(4*block))&15][words[message][block]];
    }
    uint64_t current=population_score();
    printf("{\"kind\":\"initial\",\"errors\":%llu,\"passes\":4,\"outcomes\":3145728}\n",(unsigned long long)current);
    fflush(stdout);
    int total_moves=0;
    for (int pass=0; pass<4; ++pass) {
        int moves=0;
        for (int phase=0; phase<3; ++phase) {
            for (int index=0; index<64; ++index) {
                uint8_t mask[256]={0};
                int affected[256], count=0;
                for (int message=0; message<256; ++message) {
                    for (int block=phase; block<4; block+=3)
                        if (index_for(message,block)==index) mask[message]|=(uint8_t)(1<<block);
                    if (mask[message]) affected[count++]=message;
                }
                memset(baseline,48,sizeof baseline);
                for (int message=0; message<256; ++message) {
                    if (mask[message]) continue;
                    for (int x=0; x<65536; ++x)
                        if (costs[message][x]<baseline[x]) baseline[x]=costs[message][x];
                }
                int old=labels[phase][index], selected=old;
                uint64_t best=current, scores[16];
                for (int candidate=0; candidate<16; ++candidate) {
                    if (candidate==old) {scores[candidate]=current; continue;}
                    int delta[16];
                    for (int x=0; x<16; ++x) delta[x]=one[x][candidate]-one[x][old];
                    memcpy(work,baseline,sizeof work);
                    for (int i=0; i<count; ++i) {
                        int message=affected[i], bits=mask[message];
                        for (int x=0; x<65536; ++x) {
                            int updated=costs[message][x];
                            if (bits&1) updated+=delta[x&15];
                            if (bits&2) updated+=delta[(x>>4)&15];
                            if (bits&4) updated+=delta[(x>>8)&15];
                            if (bits&8) updated+=delta[x>>12];
                            if (updated<work[x]) work[x]=(uint8_t)updated;
                        }
                    }
                    scores[candidate]=0;
                    for (int x=0; x<65536; ++x) scores[candidate]+=work[x];
                    if (scores[candidate]<best) {best=scores[candidate]; selected=candidate;}
                }
                printf("{\"kind\":\"entry\",\"pass\":%d,\"phase\":%d,\"index\":%d,\"old\":%d,\"selected\":%d,\"scores\":[",pass,phase,index,old,selected);
                for (int candidate=0; candidate<16; ++candidate)
                    printf("%s%llu",candidate ? "," : "",(unsigned long long)scores[candidate]);
                printf("]}\n");
                if (selected!=old) {
                    ++moves; ++total_moves;
                    labels[phase][index]=(uint8_t)selected;
                    int delta[16];
                    for (int x=0; x<16; ++x) delta[x]=one[x][selected]-one[x][old];
                    for (int i=0; i<count; ++i) {
                        int message=affected[i], bits=mask[message];
                        for (int block=0; block<4; ++block)
                            if (bits&(1<<block)) words[message][block]=(uint8_t)selected;
                        for (int x=0; x<65536; ++x) {
                            int updated=costs[message][x];
                            if (bits&1) updated+=delta[x&15];
                            if (bits&2) updated+=delta[(x>>4)&15];
                            if (bits&4) updated+=delta[(x>>8)&15];
                            if (bits&8) updated+=delta[x>>12];
                            costs[message][x]=(uint8_t)updated;
                        }
                    }
                    current=best;
                }
            }
        }
        uint64_t checked=population_score();
        if (checked!=current) {fprintf(stderr,"cached population mismatch\n"); return 1;}
        printf("{\"kind\":\"pass\",\"pass\":%d,\"moves\":%d,\"errors\":%llu}\n",pass,moves,(unsigned long long)current);
        fflush(stdout);
        fprintf(stderr,"pass %d: %llu errors, %d moves\n",pass,(unsigned long long)current,moves);
    }
    printf("{\"kind\":\"final\",\"errors\":%llu,\"moves\":%d,\"tables\":[",(unsigned long long)current,total_moves);
    for (int phase=0; phase<3; ++phase) {
        printf("%s[",phase ? "," : "");
        for (int index=0; index<64; ++index) printf("%s%d",index ? "," : "",labels[phase][index]);
        printf("]");
    }
    printf("]}\n");
    fprintf(stderr,"elapsed clock seconds %.6f\n",(double)(clock()-started)/CLOCKS_PER_SEC);
    return 0;
}
