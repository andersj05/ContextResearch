#define main price_search_main
#include "priced.c"
#undef main
int main(int argc,char **argv) {
    if(argc!=2) return 2;
    FILE *out=fopen(argv[1],"wb");
    if(!out) return 3;
    uint32_t values[9]={1,2,3,5,11,121,4096,1u<<20,1u<<24};
    int numerators[3]={1,2,5},denominators[3]={2,5,12};
    fputs("{\"scalar_matrix\":[",out);
    for(int x=0;x<16;++x) for(int w=0;w<16;++w)
        fprintf(out,"%s%d",x||w?",":"",scalar(x,w));
    fputs("],\"price_less_bits\":\"",out);
    for(int p=0;p<3;++p) for(int ca=0;ca<=72;++ca) for(int cb=0;cb<=72;++cb)
        for(int a=0;a<9;++a) for(int b=0;b<9;++b)
            fputc(less(ca,power(values[a],numerators[p]),cb,power(values[b],numerators[p]),denominators[p])?'1':'0',out);
    fputs("\"}\n",out);fclose(out);
    return 0;
}
