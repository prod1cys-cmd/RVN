"""Сборка книги из ведомостей UTF-8."""
import csv
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font
from openpyxl.utils import get_column_letter

ROOT = Path(__file__).resolve().parents[1]
TITLES = {
    'functional_nodes': 'Узлы', 'connections': 'Связи',
    'requirements_matrix': 'Требования', 'components': 'ЭКБ',
    'sources': 'Источники', 'signal_parameters': 'Сигналы',
    'latency_register': 'Задержки', 'timing_requirements': 'Требования по времени',
    'power_budget': 'Питание',
}

def main():
    book = Workbook()
    book.remove(book.active)
    for source in sorted((ROOT / 'analysis').glob('*.csv')):
        sheet = book.create_sheet(TITLES.get(source.stem, source.stem[:31]))
        with source.open(encoding='utf-8-sig', newline='') as stream:
            sample = stream.read(65536)
            stream.seek(0)
            delimiter = max(',;\t', key=sample.splitlines()[0].count)
            for row in csv.reader(stream, delimiter=delimiter):
                sheet.append(row)
        sheet.freeze_panes = 'B2'
        sheet.auto_filter.ref = sheet.dimensions
        for column in sheet.columns:
            width = min(72, max(12, max(len(str(cell.value or '')) for cell in column) + 2))
            sheet.column_dimensions[get_column_letter(column[0].column)].width = width
            column[0].font = Font(bold=True)
            for cell in column:
                cell.alignment = Alignment(wrap_text=True, vertical='top')
    book.save(ROOT / 'output/Ravenstvo_E2_Parameters.xlsx')

if __name__ == '__main__':
    main()
