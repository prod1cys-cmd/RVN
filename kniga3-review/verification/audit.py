"""Check the release DOCX against the bookmarks and page geometry of its PDF."""
import argparse
from collections import Counter
import json
import re
from pathlib import Path
from zipfile import ZipFile

from docx import Document
import fitz

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('docx', type=Path)
parser.add_argument('pdf', type=Path)
args=parser.parse_args()
word = Document(args.docx)
pdf = fitz.open(args.pdf)
paragraphs = word.paragraphs
titles = [p.text for p in paragraphs if p.style.name in ('Heading 1','Heading 2')]
start=next(i for i,p in enumerate(paragraphs) if p.text=='СОДЕРЖАНИЕ')
end=next(i for i,p in enumerate(paragraphs) if p.style.name=='Heading 1')
entries=dict(p.text.rsplit('\t',1) for p in paragraphs[start+1:end] if p.text)
bookmarks={heading:str(page) for _,heading,page in pdf.get_toc() if heading in titles}
assert list(entries)==titles, 'TOC headings differ from DOCX headings'
assert entries==bookmarks, 'TOC pages differ from PDF bookmarks'
captions={name:[m.group(1) for p in paragraphs if (m:=re.match(rf'^{name}\s+(\d+\.\d+)\s+[—–]',p.text))] for name in ('Рисунок','Таблица')}
for name,ids in captions.items():
    assert len(ids)==len(set(ids)), f'duplicate {name}'
    groups={}
    for item in ids:
        section,index=map(int,item.split('.'))
        groups.setdefault(section,[]).append(index)
    assert all(v==list(range(1,len(v)+1)) for v in groups.values()),(name,groups)
source_start=next(i for i,p in enumerate(paragraphs) if p.style.name=='Heading 1' and p.text=='СПИСОК ИСПОЛЬЗОВАННЫХ ИСТОЧНИКОВ')
sources=[int(m[1]) for p in paragraphs[source_start+1:] if (m:=re.match(r'^(\d+)\.',p.text))]
assert sources==list(range(1,len(sources)+1))
abstract=f'Отчёт {len(pdf)} с., кн. 3, {len(captions["Рисунок"])} рис., {len(captions["Таблица"])} табл., {len(sources)} источн.'
assert any(p.text==abstract for p in paragraphs)
assert any(abstract in ' '.join(pg.get_text().split()) for pg in pdf)
assert not any('11.7 Рабочее место' in p.text or re.search(r'\bTODO\b',p.text) for p in paragraphs)
assert '12 Рабочее место функциональных макетов' in titles
for name,ids in captions.items():
    for item in ids:
        hits=[page for page in pdf if re.search(rf'{name}\s+{re.escape(item)}\s+[—–]',page.get_text())]
        assert len(hits)==1,(name,item,len(hits))
        if name=='Рисунок':
            assert hits[0].get_image_info(),(name,item,'missing image on caption page')
fonts=set()
sparse=[]
for page in pdf:
    assert abs(page.rect.width-595.28)<1 and abs(page.rect.height-841.89)<1, page.number+1
    lines=[line.strip() for line in page.get_text().splitlines() if line.strip()]
    if page.number:
        assert lines[0]==str(page.number+1),(page.number+1,lines[:2])
    if 1<len(lines)<5 and not page.get_image_info():
        sparse.append(page.number+1)
    for f in page.get_fonts():
        fonts.add(f[3].split('+')[-1])
    for img in page.get_image_info():
        assert fitz.Rect(img['bbox']) in (page.rect+(-.5,-.5,.5,.5)), (page.number+1,img['bbox'])
assert any('TimesNewRoman' in f for f in fonts)
with ZipFile(args.docx) as z:
    assert z.testzip() is None
    assert 'word/comments.xml' not in z.namelist()
    xml=z.read('word/document.xml')
    assert b'<w:ins ' not in xml and b'<w:del ' not in xml
    equations=len(re.findall(rb'<m:oMath(?=[\s>])',xml))
print(json.dumps({'pages':len(pdf),'toc':len(entries),'figures':len(captions['Рисунок']),'tables':len(captions['Таблица']),'sources':len(sources),'editable_math':equations,'sparse_pages':sparse,'pdf_fonts':sorted(fonts)},ensure_ascii=False,indent=2))
