from pathlib import Path

source=Path('build/priced-vector/priced.c').read_text()
source=source.replace('return 4*g-sum/n;', 'return (g?4*g:log2((double)n))-sum/n;')
source=source.replace('if(g!=5 && g!=6) return 3;', 'if(g!=6) return 3;')
marker='    FILE *out=fopen(argv[2],"wb");'
addition='''    const int training=131072;
    uint32_t *sources=malloc((size_t)training*sizeof(*sources));
    uint8_t *sample_used=calloc((size_t)n,1);
    uint16_t *training_labels=malloc((size_t)training*sizeof(*training_labels));
    if(!sources || !sample_used || !training_labels) return 9;
    state=0x243f6a88u;
    int collected=0;
    while(collected<training) {
        unsigned x=draw()%(unsigned)n;
        if(!sample_used[x]) {sample_used[x]=1;sources[collected++]=x;}
    }
    int sorted=0;
    for(int x=0;x<n;++x) if(sample_used[x]) sources[sorted++]=(uint32_t)x;
    free(sample_used);
'''
assert source.count(marker)==1
source=source.replace(marker,addition+marker)
marker='    int first=1;'
addition='''    fprintf(out,"],\\"training_sources\\":%d,\\"training_source_ids\\":[",training);
    for(int t=0;t<training;++t) fprintf(out,"%s%u",t?",":"",sources[t]);
    fputs("],\\"sample_scope\\":\\"Fixed public design sample, not the full source population\\",\\"runs\\":[",out);
'''
# Replace the header's first opening runs bracket; then add sample data.
source=source.replace('\\"runs\\":[",g,n', '\\"reserved\\":[",g,n')
source=source.replace(marker,addition+marker)
start=source.index('        clock_t began=clock();')
end=source.index('        memcpy(proposal,counts,active*sizeof(*counts));')
part=source[start:end]
part=part.replace('for(int x=0;x<n;++x) {', 'for(int t=0;t<training;++t) { int x=(int)sources[t];')
part=part.replace('for(int x=0;x<n;++x) loss+=',
                  'for(int t=0;t<training;++t) { int x=(int)sources[t]; loss+=')
part=part.replace('mapping[x]', 'mapping[t]').replace('updated[x]', 'updated[t]')
part=part.replace('mapping[x]=(uint16_t)merge[mapping[x]];', 'mapping[t]=(uint16_t)merge[mapping[t]];')
part=part.replace('for(int x=0;x<n;++x) mapping[t]=',
                  'for(int t=0;t<training;++t) mapping[t]=')
part=part.replace('+mapping[t]];\n            h=entropy(counts,active,g,n);',
                  '+mapping[t]]; }\n            h=entropy(counts,active,0,training);')
part=part.replace('(double)loss/n+slope*h', '(double)loss/training+slope*h')
part=part.replace('memcpy(mapping,updated,(size_t)n*sizeof(*mapping));',
                  'memcpy(mapping,updated,(size_t)training*sizeof(*mapping));')
source=source[:start]+part+source[end:]
source=source.replace('memcpy(proposal,counts,active*sizeof(*counts));',
    'memcpy(training_labels,mapping,(size_t)training*sizeof(*mapping));\n'
    '        for(int a=0;a<active;++a) proposal[a]=counts[a]*(uint32_t)(n/training);')
source=source.replace('int differences=0;', 'int differences=0,sample_pointer=0;')
source=source.replace('differences+=chosen!=mapping[x];mapping[x]=(uint16_t)chosen;',
    'if(sample_pointer<training && sources[sample_pointer]==(uint32_t)x) {\n'
    '                differences+=chosen!=training_labels[sample_pointer];++sample_pointer;\n'
    '            }\n'
    '            mapping[x]=(uint16_t)chosen;')
source=source.replace('free(proposal);free(actual);free(ones);free(penalty);free(merge);free(weights);',
    'free(proposal);free(actual);free(ones);free(penalty);free(merge);free(weights);\n'
    '    free(sources);free(training_labels);')
Path('build/priced-vector/sampled_priced.c').write_text(source)
print('Separate sampled group-six constructor generated; original group-five source retained.')
