#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <math.h>
#include <string.h>
#include "base.h"

static uint32_t state;
static uint32_t draw(void) {
    state ^= state << 13;
    state ^= state >> 17;
    state ^= state << 5;
    return state;
}
static int bits(unsigned v) {
    int c=0;
    while (v) {c += v&1; v >>= 1;}
    return c;
}
static int scalar(int x,int a) {
    return 3*bits(x)+3*bits(a)-2*bits(x)*bits(a)+2*bits(x&a);
}
static double entropy(const uint32_t *counts,int q,int power,int n) {
    double sum=0;
    for (int a=0;a<q;++a) if (counts[a]) sum += counts[a]*log2((double)counts[a]);
    return power-sum/n;
}
int main(int argc,char **argv) {
    if (argc!=4) return 2;
    int g=atoi(argv[1]),alphabet=atoi(argv[2]);
    if (g<1 || g>4 || (alphabet!=8 && alphabet!=16)) return 3;
    int n=1 << (4*g),q=1;
    for (int i=0;i<g;++i) q*=alphabet;
    if ((uint64_t)n*q>300000000) return 4;
    const int eight[8]={0,3,5,6,9,10,12,15};
    unsigned *words=malloc(q*sizeof(*words));
    uint8_t *cost=malloc((size_t)n*q);
    uint16_t *mapping=malloc(n*sizeof(*mapping));
    uint16_t *updated=malloc(n*sizeof(*updated));
    uint32_t *counts=calloc(q,sizeof(*counts));
    double *penalty=malloc(q*sizeof(*penalty));
    int *allowed=malloc(q*sizeof(*allowed));
    if (!words || !cost || !mapping || !updated || !counts || !penalty || !allowed) return 5;
    int scalar_cost[16][16];
    for(int x=0;x<16;++x) for(int a=0;a<16;++a) scalar_cost[x][a]=scalar(x,a);
    for(int a=0;a<q;++a) {
        int v=a; unsigned w=0;
        for(int r=0;r<g;++r) {w |= (unsigned)(alphabet==8?eight[v%8]:v%16) << (4*r); v/=alphabet;}
        words[a]=w;
    }
    for(int x=0;x<n;++x) for(int a=0;a<q;++a) {
        int value=0;
        for(int r=0;r<g;++r) value+=scalar_cost[(x >> (4*r))&15][(words[a] >> (4*r))&15];
        cost[(size_t)x*q+a]=(uint8_t)value;
    }
    FILE *out=fopen(argv[3],"wb");
    if (!out) return 6;
    const double slopes[8]={.3,.35,.4,.45,.5,.6,.75,1.};
    fprintf(out,"{\"g\":%d,\"alphabet\":%d,\"n\":%d,\"q\":%d,\"runs\":[",g,alphabet,n,q);
    int first_run=1;
    for(int ti=0;ti<8;++ti) for(int seed=0;seed<8;++seed) {
        state=0x9e3779b9u+(uint32_t)seed*7919u;
        for(int a=0;a<q;++a) {allowed[a]=0;penalty[a]=0;}
        if(seed==0) for(int a=0;a<q;++a) allowed[a]=1;
        else if(seed==1) {
            for(int a=0;a<q;++a) {
                int ok=1;
                for(int r=0;r<g;++r) {int nib=(words[a] >> (4*r))&15;ok &= nib==0 || nib==15;}
                allowed[a]=ok;
            }
        } else if(seed==7 && g==3) {
            for(int a=0;a<q;++a) for(int z=0;z<64;++z) if(words[a]==base_words[z]) allowed[a]=1;
        } else {
            int target=1 << (seed+2);
            if(target>q) target=q;
            int selected=0;
            while(selected<target) {int a=(int)(draw()%(unsigned)q);if(!allowed[a]) {allowed[a]=1;++selected;}}
            for(int a=0;a<q;++a) penalty[a]=((double)(draw()%2001)-1000)/1000;
        }
        for(int x=0;x<n;++x) {
            double best=1e100; int chosen=-1;
            for(int a=0;a<q;++a) if(allowed[a]) {
                double score=cost[(size_t)x*q+a]+penalty[a];
                if(score<best) {best=score;chosen=a;}
            }
            if(chosen<0) return 7;
            mapping[x]=(uint16_t)chosen;
        }
        if(!first_run) fputc(',',out);
        first_run=0;
        fprintf(out,"{\"slope\":%.17g,\"seed\":%d,\"trajectory\":[",slopes[ti],seed);
        int stable=0,iterations=0;
        uint64_t loss=0;
        double h=0;
        for(int iteration=0;iteration<=60;++iteration) {
            memset(counts,0,q*sizeof(*counts)); loss=0;
            for(int x=0;x<n;++x) {++counts[mapping[x]];loss+=cost[(size_t)x*q+mapping[x]];}
            h=entropy(counts,q,4*g,n);
            if(iteration) fputc(',',out);
            fprintf(out,"[%llu,%.17g,%.17g]",(unsigned long long)loss,h,(double)loss/n+slopes[ti]*h);
            iterations=iteration;
            if(iteration==60) break;
            for(int a=0;a<q;++a) penalty[a]=counts[a]?-slopes[ti]*log2((double)counts[a]):1e100;
            int changes=0;
            for(int x=0;x<n;++x) {
                double best=1e100; int chosen=-1;
                for(int a=0;a<q;++a) if(counts[a]) {
                    double score=cost[(size_t)x*q+a]+penalty[a];
                    if(score<best) {best=score;chosen=a;}
                }
                updated[x]=(uint16_t)chosen;
                changes+=updated[x]!=mapping[x];
            }
            if(!changes) {stable=1;break;}
            memcpy(mapping,updated,n*sizeof(*mapping));
        }
        fprintf(out,"],\"iterations\":%d,\"stable\":%s,\"loss_sum\":%llu,\"entropy_float\":%.17g,\"mapping\":[",
                iterations,stable?"true":"false",(unsigned long long)loss,h);
        for(int x=0;x<n;++x) fprintf(out,"%s%u",x?",":"",words[mapping[x]]);
        fprintf(out,"]}");
        if(seed==7) fprintf(stderr,"g=%d alphabet=%d slope=%.3f complete\n",g,alphabet,slopes[ti]);
    }
    fputs("]}\n",out);
    fclose(out);
    free(words);free(cost);free(mapping);free(updated);free(counts);free(penalty);free(allowed);
    return 0;
}
