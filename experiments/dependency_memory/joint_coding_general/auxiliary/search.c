/* Deterministic heuristic discovery of a 64-word, three-block codebook.
 * This search supplies upper-bound witnesses, never an optimality proof.
 * Source x and decision c use successive low-to-high four-bit nibbles.
 * C grading is subsequently checked by an independent Python route executor.
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

enum { N = 4096, K = 64, MAX_SWAPS = 2 };
static uint8_t (*cost)[N];
static int book[K], present[N];

static const int endpoints[36][2] = {{0,0},{0,1},{0,2},{0,3},{0,4},{0,5},{0,6},{0,7},{1,1},{1,2},{1,3},{1,4},{1,5},{1,6},{1,7},{2,2},{2,3},{2,4},{2,5},{2,6},{2,7},{3,3},{3,4},{3,5},{3,6},{3,7},{4,4},{4,5},{4,6},{4,7},{5,5},{5,6},{5,7},{6,6},{6,7},{7,7}};
static int decoder[3][4];
static int general_loss(int r,int x,int a) {
    int result=0;
    for(int o=0;o<4;++o) {
        int word=endpoints[decoder[r][o]][(a>>o)&1], pos=0;
        for(int j=0;j<4;++j) if(j!=o) {
            result+=((x>>j)&1)!=((word>>pos)&1);++pos;
        }
    }
    return result;
}
static void costs(void) {
    uint8_t one[3][16][16];
    for(int r=0;r<3;++r) for(int x=0;x<16;++x) for(int a=0;a<16;++a)
        one[r][x][a]=(uint8_t)general_loss(r,x,a);
    cost=malloc((size_t)N*sizeof(*cost));
    if(!cost) {fprintf(stderr,"allocation failed\n");exit(2);}
    for(int c=0;c<N;++c) for(int x=0;x<N;++x)
        cost[c][x]=one[0][x&15][c&15]+one[1][(x>>4)&15][(c>>4)&15]+one[2][x>>8][c>>8];
}

static int grade(const uint8_t best[N]) {
    int result = 0;
    for (int x = 0; x < N; ++x) result += best[x];
    return result;
}

static int with_candidate(const uint8_t base[N], int candidate) {
    int result = 0;
    for (int x = 0; x < N; ++x)
        result += base[x] < cost[candidate][x] ? base[x] : cost[candidate][x];
    return result;
}

static void nearest(uint8_t best[N], int omitted, int count) {
    memset(best, 36, N);
    for (int m = 0; m < count; ++m) if (m != omitted)
        for (int x = 0; x < N; ++x)
            if (cost[book[m]][x] < best[x]) best[x] = cost[book[m]][x];
}

static void greedy(void) {
    uint8_t best[N];
    memset(best, 36, N);
    printf("\"greedy_steps\":[");
    for (int m = 0; m < K; ++m) {
        int choice = -1, value = N * 36 + 1;
        for (int c = 0; c < N; ++c) if (!present[c]) {
            int candidate = with_candidate(best, c);
            if (candidate < value) { choice = c; value = candidate; }
        }
        book[m] = choice;
        present[choice] = 1;
        for (int x = 0; x < N; ++x)
            if (cost[choice][x] < best[x]) best[x] = cost[choice][x];
        printf("%s[%d,%d]", m ? "," : "", choice, value);
    }
    printf("],");
}

static void concatenation(void) {
    const int solo[] = {0, 1, 14, 15};
    const int ties[] = {3, 5, 6, 9, 10, 12};
    int m = 0;
    for (int c = 0; c < 4; ++c) {
        for (int a = 0; a < 2; ++a)
            for (int b = 0; b < 4; ++b)
                book[m++] = (a ? 15 : 0) + 16 * solo[b] + 256 * solo[c];
        book[m++] = 1 + 16 * 15 + 256 * solo[c];
        book[m++] = 14 + 16 * 15 + 256 * solo[c];
        for (int a = 0; a < 6; ++a) book[m++] = ties[a] + 256 * solo[c];
    }
    for (int i = 0; i < K; ++i) present[book[i]] = 1;
    printf("\"greedy_steps\":[],");
}

static int integer_compare(const void *a, const void *b) {
    return (*(const int *)a > *(const int *)b) - (*(const int *)a < *(const int *)b);
}

int main(int argc, char **argv) {
    if(argc!=4) {fprintf(stderr,"usage: search decoder1 decoder2 decoder3\n");return 2;}
    int indices[3];
    for(int r=0;r<3;++r) {
        char *end=NULL;long value=strtol(argv[r+1],&end,10);
        if(!end || *end || value<0 || value>=1679616) {fprintf(stderr,"invalid decoder index\n");return 2;}
        indices[r]=(int)value;
        for(int o=0;o<4;++o) {decoder[r][o]=(int)(value%36);value/=36;}
    }
    clock_t started=clock();costs();
    printf("{\"version\":\"finite3_general_heuristic_v1\",\"decoder_indices\":[%d,%d,%d],",indices[0],indices[1],indices[2]);
    greedy();
    uint8_t best[N], base[N];
    nearest(best, -1, K);
    int initial = grade(best), current = initial, exhausted = 0;
    printf("\"initial_errors\":%d,\"accepted_swaps\":[", initial);
    int accepted = 0;
    for (int pass = 0; pass < MAX_SWAPS; ++pass) {
        int position = -1, replacement = -1, target = current;
        for (int m = 0; m < K; ++m) {
            nearest(base, m, K);
            for (int c = 0; c < N; ++c) if (!present[c]) {
                int value = with_candidate(base, c);
                if (value < target) { target = value; position = m; replacement = c; }
            }
        }
        if (position < 0) { exhausted = 1; break; }
        int removed = book[position];
        printf("%s[%d,%d,%d]", accepted ? "," : "", removed, replacement, target);
        present[removed] = 0;
        present[replacement] = 1;
        book[position] = replacement;
        current = target;
        ++accepted;
        fflush(stdout);
    }
    printf("],\"max_swaps\":%d,\"single_swap_exhausted\":%s,\"errors\":%d,\"codeword_ids\":[",
           MAX_SWAPS, exhausted ? "true" : "false", current);
    qsort(book, K, sizeof(book[0]), integer_compare);
    for (int m = 0; m < K; ++m) printf("%s%d", m ? "," : "", book[m]);
    printf("],\"c_clock_seconds\":%.6f,\"outcomes\":147456}\n", (double)(clock() - started) / CLOCKS_PER_SEC);
    free(cost);
    return 0;
}
