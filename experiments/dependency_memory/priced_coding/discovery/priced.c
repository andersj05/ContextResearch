#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <math.h>
#include <string.h>
#include <time.h>
#include "base.h"

typedef unsigned __int128 wide;
static uint32_t state;
static uint32_t draw(void) {
    state ^= state << 13; state ^= state >> 17; state ^= state << 5;
    return state;
}
static int bits(unsigned v) {return __builtin_popcount(v);}
static int scalar(int x,int a) {
    return 3*bits(x)+3*bits(a)-2*bits(x)*bits(a)+2*bits(x&a);
}
static int wide_bits(wide v) {
    uint64_t upper=(uint64_t)(v>>64);
    return upper?128-__builtin_clzll(upper):64-__builtin_clzll((uint64_t)v);
}
static wide power(uint32_t v,int a) {
    wide result=1;
    for(int i=0;i<a;++i) result*=v;
    return result;
}
static int less(int cost,wide weight,int best_cost,wide best_weight,int b) {
    int shift=b*abs(cost-best_cost);
    if(cost>=best_cost) {
        if(wide_bits(best_weight)+shift>wide_bits(weight)) return 0;
        return (best_weight<<shift)<weight;
    }
    if(wide_bits(weight)+shift>wide_bits(best_weight)) return 1;
    return (weight<<shift)>best_weight;
}
static double entropy(const uint32_t *counts,int q,int g,int n) {
    double sum=0;
    for(int a=0;a<q;++a) if(counts[a]) sum+=counts[a]*log2((double)counts[a]);
    return 4*g-sum/n;
}
static void fill(int a,unsigned w,int q,int left_g,int right_g,
                 uint8_t *left,uint8_t *right,int d[16][16]) {
    for(int x=0;x<(1<<(4*left_g));++x) {
        int value=0;
        for(int r=0;r<left_g;++r) value+=d[(x>>(4*r))&15][(w>>(4*r))&15];
        left[(size_t)x*q+a]=(uint8_t)value;
    }
    for(int x=0;x<(1<<(4*right_g));++x) {
        int value=0;
        for(int r=0;r<right_g;++r) value+=d[(x>>(4*r))&15][(w>>(4*(r+left_g)))&15];
        right[(size_t)x*q+a]=(uint8_t)value;
    }
}
int main(int argc,char **argv) {
    if(argc!=3) return 2;
    int g=atoi(argv[1]);
    if(g!=5 && g!=6) return 3;
    int n=1<<(4*g),q=g==5?8192:16384;
    int lg=g/2,rg=g-lg,ln=1<<(4*lg),rn=1<<(4*rg),mask=ln-1;
    uint64_t workspace=(uint64_t)(ln+rn)*q+2*(uint64_t)n*sizeof(uint16_t)+
        (uint64_t)q*(2*sizeof(unsigned)+3*sizeof(uint32_t)+2*sizeof(double)+sizeof(int)+sizeof(wide)+4*g*sizeof(uint32_t));
    if(workspace>268435456) return 4;
    int d[16][16];
    for(int x=0;x<16;++x) for(int a=0;a<16;++a) d[x][a]=scalar(x,a);
    unsigned *words=malloc(q*sizeof(*words)),*previous=malloc(q*sizeof(*previous));
    uint8_t *left=malloc((size_t)ln*q),*right=malloc((size_t)rn*q);
    uint16_t *mapping=malloc((size_t)n*sizeof(*mapping)),*updated=malloc((size_t)n*sizeof(*updated));
    uint32_t *counts=calloc(q,sizeof(*counts)),*proposal=malloc(q*sizeof(*proposal));
    uint32_t *actual=calloc(q,sizeof(*actual)),*ones=calloc((size_t)q*g*4,sizeof(*ones));
    double *penalty=malloc(q*sizeof(*penalty));
    int *merge=malloc(q*sizeof(*merge));
    wide *weights=malloc(q*sizeof(*weights));
    if(!words || !previous || !left || !right || !mapping || !updated || !counts ||
       !proposal || !actual || !ones || !penalty || !merge || !weights) return 5;
    FILE *out=fopen(argv[2],"wb");
    if(!out) return 6;
    fprintf(out,"{\"g\":%d,\"population\":%d,\"temporary_workspace_bytes\":%llu,\"runs\":[",g,n,(unsigned long long)workspace);
    int first=1;
    for(int ti=0;ti<(g==5?2:1);++ti) for(int seed=0;seed<4;++seed) {
        if(g==6 && seed!=0 && seed!=3) continue;
        int pa=ti?1:2,pb=ti?2:5;
        double slope=(double)pa/pb;
        state=0x9e3779b9u+(uint32_t)seed*7919u;
        int active=0;
        if(seed==0) {
            if(g==5) {
                const unsigned pair[4]={0,255,15,240};
                for(int z=0;z<64;++z) for(int t=0;t<4;++t)
                    words[active++]=base_words[z]|(pair[t]<<12);
            } else for(int z=0;z<64;++z) for(int t=0;t<64;++t)
                words[active++]=base_words[z]|(base_words[t]<<12);
        } else {
            int target=g==5?(seed==1?1024:seed==2?4096:8192):
                             (seed==1?4096:seed==2?8192:16384);
            uint8_t *used=calloc((size_t)n,1);
            if(!used) return 7;
            while(active<target) {
                unsigned w=draw()%(unsigned)n;
                if(!used[w]) {used[w]=1;words[active++]=w;}
            }
            free(used);
        }
        for(int a=0;a<active;++a) {
            penalty[a]=seed?((double)(draw()%2001)-1000)/1000:0.;
            fill(a,words[a],q,lg,rg,left,right,d);
        }
        clock_t began=clock();
        for(int x=0;x<n;++x) {
            double best=1e100;int chosen=-1;
            for(int a=0;a<active;++a) {
                int cost=left[(size_t)(x&mask)*q+a]+right[(size_t)(x>>(4*lg))*q+a];
                double score=cost+penalty[a];
                if(score<best) {best=score;chosen=a;}
            }
            mapping[x]=(uint16_t)chosen;
        }
        if(!first) fputc(',',out);first=0;
        fprintf(out,"{\"price\":[%d,%d],\"seed\":%d,\"initial_words\":%d,\"trajectory\":[",pa,pb,seed,active);
        uint64_t loss=0;double h=0;int stable=0,iterations=0;
        for(int it=0;it<=60;++it) {
            memset(counts,0,q*sizeof(*counts));
            memset(ones,0,(size_t)q*g*4*sizeof(*ones));
            for(int x=0;x<n;++x) {
                int a=mapping[x];++counts[a];
                for(int r=0;r<g;++r) for(int j=0;j<4;++j)
                    ones[((size_t)a*g+r)*4+j]+=(x>>(4*r+j))&1;
            }
            memcpy(previous,words,active*sizeof(*words));
            for(int a=0;a<active;++a) if(counts[a]) {
                unsigned w=0;
                for(int r=0;r<g;++r) {
                    uint32_t total=0;
                    for(int j=0;j<4;++j) total+=ones[((size_t)a*g+r)*4+j];
                    for(int o=0;o<4;++o)
                        if(2*(total-ones[((size_t)a*g+r)*4+o])>3*counts[a]) w|=1u<<(4*r+o);
                }
                words[a]=w;
            }
            for(int a=0;a<active;++a) {
                merge[a]=a;
                if(counts[a]) for(int b=0;b<a;++b) if(counts[b] && words[a]==words[b]) {
                    merge[a]=merge[b];counts[merge[a]]+=counts[a];counts[a]=0;break;
                }
            }
            for(int x=0;x<n;++x) mapping[x]=(uint16_t)merge[mapping[x]];
            for(int a=0;a<active;++a) if(counts[a] && words[a]!=previous[a])
                fill(a,words[a],q,lg,rg,left,right,d);
            loss=0;
            for(int x=0;x<n;++x) loss+=left[(size_t)(x&mask)*q+mapping[x]]+right[(size_t)(x>>(4*lg))*q+mapping[x]];
            h=entropy(counts,active,g,n);
            if(it) fputc(',',out);
            fprintf(out,"[%llu,%.17g,%.17g]",(unsigned long long)loss,h,(double)loss/n+slope*h);
            iterations=it;
            if(!(it%5)) fprintf(stderr,"g=%d price=%d/%d seed=%d iteration=%d active-loss=%llu H=%.8f\n",g,pa,pb,seed,it,(unsigned long long)loss,h);
            if(it==60) break;
            for(int a=0;a<active;++a) penalty[a]=counts[a]?-slope*log2((double)counts[a]):1e100;
            int changes=0;
            for(int x=0;x<n;++x) {
                double best=1e100;int chosen=-1;
                for(int a=0;a<active;++a) if(counts[a]) {
                    double score=left[(size_t)(x&mask)*q+a]+right[(size_t)(x>>(4*lg))*q+a]+penalty[a];
                    if(score<best) {best=score;chosen=a;}
                }
                updated[x]=(uint16_t)chosen;changes+=updated[x]!=mapping[x];
            }
            if(!changes) {stable=1;break;}
            memcpy(mapping,updated,(size_t)n*sizeof(*mapping));
        }
        memcpy(proposal,counts,active*sizeof(*counts));memset(actual,0,q*sizeof(*actual));
        for(int a=0;a<active;++a) if(proposal[a]) weights[a]=power(proposal[a],pa);
        int fallback=-1;
        for(int a=0;a<active;++a) if(proposal[a] && (fallback<0 || proposal[a]>proposal[fallback])) fallback=a;
        uint64_t exact_loss=0,comparisons=0;int differences=0;
        for(int x=0;x<n;++x) {
            int chosen=-1,best_cost=0;
            for(int a=0;a<active;++a) if(proposal[a]) {
                int cost=left[(size_t)(x&mask)*q+a]+right[(size_t)(x>>(4*lg))*q+a];
                ++comparisons;
                if(chosen<0 || less(cost,weights[a],best_cost,weights[chosen],pb)) {chosen=a;best_cost=cost;}
            }
            int fallback_cost=left[(size_t)(x&mask)*q+fallback]+right[(size_t)(x>>(4*lg))*q+fallback];
            if(best_cost>fallback_cost) return 8;
            ++actual[chosen];exact_loss+=best_cost;
            differences+=chosen!=mapping[x];mapping[x]=(uint16_t)chosen;
        }
        int *renumber=malloc(active*sizeof(*renumber));int final=0;
        for(int a=0;a<active;++a) renumber[a]=proposal[a]?final++:-1;
        fprintf(out,"],\"stable_float_proposal\":%s,\"iterations\":%d,\"float_loss_sum\":%llu,\"float_entropy\":%.17g,"
                    "\"exact_loss_sum\":%llu,\"exact_entropy_float\":%.17g,\"exact_price_comparisons\":%llu,"
                    "\"changed_float_assignments\":%d,\"fallback_index\":%d,\"final_words\":%d,\"words\":[",
            stable?"true":"false",iterations,(unsigned long long)loss,h,(unsigned long long)exact_loss,
            entropy(actual,active,g,n),(unsigned long long)comparisons,differences,renumber[fallback],final);
        int comma=0;
        for(int a=0;a<active;++a) if(proposal[a]) fprintf(out,"%s%u",comma++?",":"",words[a]);
        fputs("],\"proposal_counts\":[",out);comma=0;
        for(int a=0;a<active;++a) if(proposal[a]) fprintf(out,"%s%u",comma++?",":"",proposal[a]);
        fputs("],\"counts\":[",out);comma=0;
        for(int a=0;a<active;++a) if(proposal[a]) fprintf(out,"%s%u",comma++?",":"",actual[a]);
        fputs("],\"mapping\":[",out);
        for(int x=0;x<n;++x) fprintf(out,"%s%d",x?",":"",renumber[mapping[x]]);
        fprintf(out,"],\"c_clock_elapsed_seconds\":%.17g,\"c_clock_scope\":\"Platform-dependent C runtime clock, exploratory only\"}",(double)(clock()-began)/CLOCKS_PER_SEC);
        free(renumber);fflush(out);
        fprintf(stderr,"g=%d price=%d/%d seed=%d exact final words=%d loss=%llu H=%.8f changes=%d\n",g,pa,pb,seed,final,(unsigned long long)exact_loss,entropy(actual,active,g,n),differences);
    }
    fputs("]}\n",out);fclose(out);
    free(words);free(previous);free(left);free(right);free(mapping);free(updated);free(counts);
    free(proposal);free(actual);free(ones);free(penalty);free(merge);free(weights);
    return 0;
}
