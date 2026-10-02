#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <math.h>
#include <string.h>
#include <time.h>
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
    while(v) {c+=v&1;v>>=1;}
    return c;
}
static int scalar(int x,int a) {
    return 3*bits(x)+3*bits(a)-2*bits(x)*bits(a)+2*bits(x&a);
}
static double entropy(const uint32_t *counts,int q,int power,int n) {
    double sum=0;
    for(int a=0;a<q;++a) if(counts[a]) sum+=counts[a]*log2((double)counts[a]);
    return power-sum/n;
}
int main(int argc,char **argv) {
    if(argc!=3) return 2;
    int g=atoi(argv[1]);
    if(g<3 || g>4) return 3;
    int n=1 << (4*g),q=1024;
    int d[16][16];
    for(int x=0;x<16;++x) for(int a=0;a<16;++a) d[x][a]=scalar(x,a);
    unsigned *words=malloc(q*sizeof(*words));
    unsigned *previous=malloc(q*sizeof(*previous));
    uint8_t *cost=malloc((size_t)n*q);
    uint16_t *mapping=malloc(n*sizeof(*mapping));
    uint16_t *updated=malloc(n*sizeof(*updated));
    uint32_t *counts=calloc(q,sizeof(*counts));
    uint32_t *ones=calloc((size_t)q*g*4,sizeof(*ones));
    double *penalty=malloc(q*sizeof(*penalty));
    int *merge=malloc(q*sizeof(*merge));
    if(!words || !previous || !cost || !mapping || !updated || !counts || !ones || !penalty || !merge) return 4;
    FILE *out=fopen(argv[2],"wb");
    if(!out) return 5;
    const double slopes[12]={.15,.2,.25,.3,.35,.4,.45,.5,.6,.75,1.,1.5};
    const unsigned scalar_base[4]={0,1,14,15};
    clock_t began=clock();
    fprintf(out,"{\"g\":%d,\"alphabet\":16,\"n\":%d,\"method\":\"centroid-updating ECVQ\",\"runs\":[",g,n);
    int first=1;
    for(int ti=0;ti<12;++ti) for(int seed=0;seed<8;++seed) {
        state=0x9e3779b9u+(uint32_t)seed*7919u;
        int active=0;
        if(seed==0) {
            for(int z=0;z<64;++z) for(int s=0;s<(g==3?1:4);++s)
                words[active++]=base_words[z]|(g==4?scalar_base[s]<<12:0);
        } else if(seed==1) {
            for(int a=0;a<(1 << g);++a) {
                unsigned w=0;
                for(int r=0;r<g;++r) w|=((a>>r)&1?15u:0u)<<(4*r);
                words[active++]=w;
            }
        } else {
            int target=1 << (seed+3);
            while(active<target) {
                unsigned w=draw()%(unsigned)n;
                int duplicate=0;
                for(int a=0;a<active;++a) duplicate|=words[a]==w;
                if(!duplicate) words[active++]=w;
            }
        }
        for(int a=0;a<active;++a) {
            penalty[a]=seed>=2?((double)(draw()%2001)-1000)/1000:0.;
            for(int x=0;x<n;++x) {
                int value=0;
                for(int r=0;r<g;++r) value+=d[(x>>(4*r))&15][(words[a]>>(4*r))&15];
                cost[(size_t)x*q+a]=(uint8_t)value;
            }
        }
        for(int x=0;x<n;++x) {
            double best=1e100;
            int chosen=-1;
            for(int a=0;a<active;++a) {
                double score=cost[(size_t)x*q+a]+penalty[a];
                if(score<best) {best=score;chosen=a;}
            }
            mapping[x]=(uint16_t)chosen;
        }
        if(!first) fputc(',',out);
        first=0;
        fprintf(out,"{\"slope\":%.17g,\"seed\":%d,\"initial_words\":%d,\"trajectory\":[",slopes[ti],seed,active);
        uint64_t loss=0;
        double h=0;
        int stable=0,iterations=0;
        for(int it=0;it<=80;++it) {
            memset(counts,0,q*sizeof(*counts));
            memset(ones,0,(size_t)q*g*4*sizeof(*ones));
            for(int x=0;x<n;++x) {
                int a=mapping[x];
                ++counts[a];
                for(int r=0;r<g;++r) for(int j=0;j<4;++j)
                    ones[((size_t)a*g+r)*4+j]+=(x>>(4*r+j))&1;
            }
            memcpy(previous,words,active*sizeof(*words));
            for(int a=0;a<active;++a) if(counts[a]) {
                unsigned w=0;
                for(int r=0;r<g;++r) {
                    uint32_t total=0;
                    for(int j=0;j<4;++j) total+=ones[((size_t)a*g+r)*4+j];
                    for(int o=0;o<4;++o) if(2*(total-ones[((size_t)a*g+r)*4+o])>3*counts[a])
                        w|=1u<<(4*r+o);
                }
                words[a]=w;
            }
            for(int a=0;a<active;++a) {
                merge[a]=a;
                if(counts[a]) for(int b=0;b<a;++b) if(counts[b] && words[a]==words[b]) {
                    merge[a]=merge[b];
                    counts[merge[a]]+=counts[a];
                    counts[a]=0;
                    break;
                }
            }
            for(int x=0;x<n;++x) mapping[x]=(uint16_t)merge[mapping[x]];
            for(int a=0;a<active;++a) if(counts[a] && words[a]!=previous[a])
                for(int x=0;x<n;++x) {
                    int value=0;
                    for(int r=0;r<g;++r) value+=d[(x>>(4*r))&15][(words[a]>>(4*r))&15];
                    cost[(size_t)x*q+a]=(uint8_t)value;
                }
            loss=0;
            for(int x=0;x<n;++x) loss+=cost[(size_t)x*q+mapping[x]];
            h=entropy(counts,active,4*g,n);
            if(it) fputc(',',out);
            fprintf(out,"[%llu,%.17g,%.17g]",(unsigned long long)loss,h,(double)loss/n+slopes[ti]*h);
            iterations=it;
            if(it==80) break;
            for(int a=0;a<active;++a) penalty[a]=counts[a]?-slopes[ti]*log2((double)counts[a]):1e100;
            int changes=0;
            for(int x=0;x<n;++x) {
                double best=1e100;
                int chosen=-1;
                for(int a=0;a<active;++a) if(counts[a]) {
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
        fputs("]}",out);
        if(seed==7) fprintf(stderr,"g=%d centroid slope=%.3f complete\n",g,slopes[ti]);
    }
    fprintf(out,"],\"c_clock_elapsed_seconds\":%.17g,\"c_clock_scope\":\"C runtime clock, platform dependent; exploratory only\"}\n",(double)(clock()-began)/CLOCKS_PER_SEC);
    fclose(out);
    free(words);free(previous);free(cost);free(mapping);free(updated);free(counts);free(ones);free(penalty);free(merge);
    return 0;
}
