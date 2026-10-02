from pathlib import Path
from experiments.dependency_memory.conditional_coding.codec import BASE
Path('build/entropy-vector/base.h').write_text(
    'static const unsigned base_words[64]={'+','.join(map(str,BASE))+'};\n')
