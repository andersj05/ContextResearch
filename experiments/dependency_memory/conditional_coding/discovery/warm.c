#define main original_lloyd_main
#include "search.c"
#undef main

int main(void) {
    initialize();
    for (int b=0; b<64; ++b) {
        right[b]=BASE[b];
        for (int a=0; a<64; ++a) left[b][a]=BASE[a];
    }
    left[52][40]=1619;
    uint64_t previous=UINT64_MAX;
    for (int step=0; step<=8; ++step) {
        uint64_t errors=evaluate();
        if (errors>previous) {fprintf(stderr,"warm loss increased\n"); return 2;}
        previous=errors;
        printf("{\"kind\":\"warm\",\"step\":%d,\"errors\":%llu,\"outcomes\":1207959552}\n",step,(unsigned long long)errors);
        fflush(stdout);
        fprintf(stderr,"warm step %d: %llu\n",step,(unsigned long long)errors);
        if (step<8) {
            for (int b=0; b<64; ++b) {
                right[b]=modal(right[b],right_margins[b]);
                for (int a=0; a<64; ++a) left[b][a]=modal(left[b][a],left_margins[b][a]);
            }
        }
    }
    printf("{\"kind\":\"final\",\"errors\":%llu,\"right\":",(unsigned long long)previous);
    print_book(right); printf(",\"left\":[");
    for (int b=0; b<64; ++b) {if (b) printf(","); print_book(left[b]);}
    printf("]}\n");
    return 0;
}
