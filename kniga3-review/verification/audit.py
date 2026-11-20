"""Check the release DOCX against the bookmarks and page geometry of its PDF."""
import argparse
from decimal import Decimal
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
bibliography_page = int(bookmarks['СПИСОК ИСПОЛЬЗОВАННЫХ ИСТОЧНИКОВ']) - 1
printed_sources = [
    int(match[1])
    for page in list(pdf)[bibliography_page:]
    for block in page.get_text('blocks')
    if abs(block[0] - word.sections[0].left_margin.pt) < 2
    and (match := re.match(r'^(\d+)\.\s', block[4]))
]
assert printed_sources == sources, 'Bibliography numbers differ in PDF'
bibliography = paragraphs[source_start+1:]
assert all(
    p.paragraph_format.keep_together is True and p.paragraph_format.line_spacing == 1.5
    for p in bibliography
), 'Bibliography typography is inconsistent'
assert all(
    not re.search(r'АРБМ\.|Протокол технического совещания|POS26|Коммерческое предложение', p.text)
    for p in bibliography
), 'Internal material listed as an external source'
source_ref = re.compile(r'\[([0-9]+(?:[–-][0-9]+)?(?:,\s*[0-9]+(?:[–-][0-9]+)?)*)\]')
body_texts = [p.text for p in paragraphs[:source_start]]
body_texts.extend(c.text for t in word.tables for row in t.rows for c in row.cells)
for body in body_texts:
    for group in source_ref.findall(body):
        for value in re.findall(r'\d+', group):
            assert int(value) in sources, ('Invalid source reference', group)
selection = next(i for i,p in enumerate(paragraphs) if p.style.name == 'Heading 2' and p.text.endswith('Сравнение и выбор элементной базы'))
structure = next(i for i,p in enumerate(paragraphs) if p.style.name == 'Heading 2' and p.text.endswith('Структура модуля'))
assert selection < structure
assert not any(re.search(r'\b(?:DD|DA)\d+\b', p.text) for p in paragraphs[selection:structure])

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
checks = next(
    table for table in word.tables
    if table.cell(0, 0).text == 'Код' and table.cell(1, 0).text == 'П-01'
)
assert [row.cells[0].text for row in checks.rows[1:]] == [
    f'П-{index:02}' for index in range(1, 12)
]
assert '51 дБ' in checks.cell(3, 2).text and '47 дБ' in checks.cell(10, 2).text
cost = next(
    table for table in word.tables
    if table.cell(0, 0).text == '№' and table.cell(0, 1).text == 'Компонент'
)
amounts = []
for row in cost.rows[1:-1]:
    quantity, unit_price, total = (
        Decimal(''.join(cell.text.split()).replace(',', '.')) for cell in row.cells[2:]
    )
    assert quantity * unit_price == total
    amounts.append(total)
assert sum(amounts) == Decimal(''.join(cost.rows[-1].cells[-1].text.split()).replace(',', '.'))
section = word.sections[0]
left_margin = section.left_margin.pt
right_margin = section.right_margin.pt
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
        box = fitz.Rect(img['bbox'])
        assert box in (page.rect+(-.5,-.5,.5,.5)), (page.number+1,img['bbox'])
        assert box.x0 >= left_margin-3 and box.x1 <= page.rect.width-right_margin+3, (
            page.number+1, 'Image exceeds text area', img['bbox']
        )
assert any('TimesNewRoman' in f for f in fonts)
with ZipFile(args.docx) as z:
    assert z.testzip() is None
    assert 'word/comments.xml' not in z.namelist()
    xml=z.read('word/document.xml')
    assert b'<w:ins ' not in xml and b'<w:del ' not in xml
    equations=len(re.findall(rb'<m:oMath(?=[\s>])',xml))
print(json.dumps({'pages':len(pdf),'toc':len(entries),'figures':len(captions['Рисунок']),'tables':len(captions['Таблица']),'sources':len(sources),'editable_math':equations,'sparse_pages':sparse,'pdf_fonts':sorted(fonts)},ensure_ascii=False,indent=2))
