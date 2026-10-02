/* Independent tensor min-plus check, with literal omitted/query losses.
   No inclusion of the discovery program, its chunks, or its comparator. */
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

typedef unsigned __int128 integer;
static uint64_t logarithm[16384];
static integer weight[16384];
static int denominator;
static uint64_t comparisons, close_comparisons;

static int precedes(uint8_t cost, uint16_t id, uint8_t best_cost, uint16_t best) {
    ++comparisons;
    if (best == 65535) return 1;
    if (weight[id] == weight[best])
        return cost < best_cost || (cost == best_cost && id < best);
    int64_t score = ((int64_t)denominator*cost << 32)-(int64_t)logarithm[id];
    int64_t best_score = ((int64_t)denominator*best_cost << 32)-(int64_t)logarithm[best];
    if (score < best_score-1) return 1;
    if (score > best_score+1) return 0;
    ++close_comparisons;
    int shift = denominator*abs((int)cost-best_cost);
    /* q^a <= 2^48 and near fixed-point scores imply shift <= 49.
       This independent broad guard also prevents undefined shifts. */
    if (shift > 64) {fprintf(stderr,"Impossible near-score shift\n");exit(12);}
    integer left = weight[best], right = weight[id];
    if (cost >= best_cost) left <<= shift;
    else right <<= shift;
    return left < right || (left == right && id < best);
}

int main(int argc, char **argv) {
    if (argc != 4) return 2;
    FILE *descriptor = fopen(argv[1],"rb");
    if (!descriptor) return 3;
    int g, q, numerator;
    if (fscanf(descriptor,"%d %d %d %d",&g,&q,&numerator,&denominator) != 4 ||
        g < 1 || g > 6 || q < 1 || q > 16384 || numerator < 1 || numerator > 2 ||
        denominator < 1 || denominator > 5) return 4;
    uint32_t n = 1u << (4*g);
    uint16_t *labels = malloc((size_t)n*sizeof(*labels));
    uint16_t *next_labels = malloc((size_t)n*sizeof(*next_labels));
    uint8_t *costs = calloc(n,1), *next_costs = malloc(n);
    uint32_t *counts = calloc(q,sizeof(*counts));
    if (!labels || !next_labels || !costs || !next_costs || !counts) return 5;
    memset(labels,255,(size_t)n*sizeof(*labels));
    for (int id=0; id<q; ++id) {
        uint32_t word, prior;
        unsigned long long fixed;
        if (fscanf(descriptor,"%u %u %llu",&word,&prior,&fixed) != 3 ||
            word >= n || !prior || prior > n || labels[word] != 65535) return 6;
        labels[word] = (uint16_t)id;
        logarithm[id] = fixed;
        weight[id] = numerator == 1 ? prior : (integer)prior*prior;
    }
    fclose(descriptor);
    int loss[16][16];
    for (int x=0; x<16; ++x) for (int w=0; w<16; ++w) {
        int value = 0;
        for (int omitted=0; omitted<4; ++omitted)
            for (int query=0; query<4; ++query) if (query != omitted)
                value += ((x>>query)&1) != ((w>>omitted)&1);
        loss[x][w] = value;
    }
    clock_t began = clock();
    uint64_t reachable[6];
    for (int r=0; r<g; ++r) {
        uint32_t stride = 1u << (4*r), chunk = 16*stride;
        uint64_t reached = 0;
        for (uint32_t base=0; base<n; base+=chunk) for (uint32_t offset=0; offset<stride; ++offset) {
            uint16_t ids[16]; uint8_t old_costs[16]; int any=0;
            for (int w=0; w<16; ++w) {
                uint32_t at = base+offset+w*stride;
                ids[w] = labels[at]; old_costs[w] = costs[at]; any |= ids[w] != 65535;
            }
            for (int x=0; x<16; ++x) {
                uint16_t best=65535; uint8_t best_cost=0;
                if (any) for (int w=0; w<16; ++w) if (ids[w] != 65535) {
                    uint8_t value = old_costs[w]+loss[x][w];
                    if (precedes(value,ids[w],best_cost,best)) {best=ids[w];best_cost=value;}
                }
                uint32_t at = base+offset+x*stride;
                next_labels[at]=best; next_costs[at]=best_cost; reached += best != 65535;
            }
        }
        uint16_t *id_swap=labels; labels=next_labels; next_labels=id_swap;
        uint8_t *cost_swap=costs; costs=next_costs; next_costs=cost_swap;
        reachable[r]=reached;
        fprintf(stderr,"g=%d dimension=%d/%d reachable=%llu comparisons=%llu\n",
            g,r+1,g,(unsigned long long)reached,(unsigned long long)comparisons);
    }
    FILE *expected=fopen(argv[2],"rb");
    if (!expected) return 7;
    uint64_t mismatches=0,total_loss=0;
    for (uint32_t x=0; x<n; ++x) {
        int lo=fgetc(expected), hi=fgetc(expected);
        if (lo==EOF || hi==EOF || labels[x]==65535) return 8;
        mismatches += labels[x] != (lo|(hi<<8));
        ++counts[labels[x]];total_loss+=costs[x];
    }
    if (fgetc(expected)!=EOF) return 9;
    fclose(expected);
    FILE *out=fopen(argv[3],"wb");
    if (!out) return 10;
    fprintf(out,"{\"g\":%d,\"source_population\":%u,\"book_words\":%d,"
        "\"tensor_comparisons\":%llu,\"near_score_exact_comparisons\":%llu,"
        "\"mismatches\":%llu,\"exact_loss_sum\":%llu,\"reachable_states\":[",
        g,n,q,(unsigned long long)comparisons,(unsigned long long)close_comparisons,
        (unsigned long long)mismatches,(unsigned long long)total_loss);
    for (int r=0;r<g;++r) fprintf(out,"%s%llu",r?",":"",(unsigned long long)reachable[r]);
    fputs("],\"counts\":[",out);
    for (int id=0;id<q;++id) fprintf(out,"%s%u",id?",":"",counts[id]);
    fprintf(out,"],\"temporary_array_bytes\":%llu,\"c_clock_elapsed_seconds\":%.17g,"
        "\"c_clock_scope\":\"Platform-dependent runtime clock, one checker sample\"}\n",
        (unsigned long long)(6*(uint64_t)n+q*sizeof(*counts)),
        (double)(clock()-began)/CLOCKS_PER_SEC);
    fclose(out);
    free(labels);free(next_labels);free(costs);free(next_costs);free(counts);
    return mismatches ? 11 : 0;
}
