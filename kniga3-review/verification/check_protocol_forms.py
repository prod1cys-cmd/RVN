#!/usr/bin/env python3
"""Сводка заполненности стандартных бланков К-01–К-22 по XML DOCX."""

import argparse
import csv
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET
import zipfile


NAMESPACES = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
MEASUREMENT_HEADINGS = ("Измеренное значение", "Погрешность", "Вывод")


def visible_text(element):
    return "".join(node.text or "" for node in element.findall(".//w:t", NAMESPACES)).strip()


def inspect_protocol(path):
    with zipfile.ZipFile(path) as document:
        body = ET.fromstring(document.read("word/document.xml")).find("w:body", NAMESPACES)

    for table in body.findall("w:tbl", NAMESPACES):
        rows = [
            [visible_text(cell) for cell in row.findall("w:tc", NAMESPACES)]
            for row in table.findall("w:tr", NAMESPACES)
        ]
        if rows and tuple(rows[0][-3:]) == MEASUREMENT_HEADINGS:
            fields = [row[-3:] for row in rows[1:]]
            break
    else:
        raise ValueError(f"Таблица результатов отсутствует: {path}")

    conclusions = [
        text
        for paragraph in body.findall("w:p", NAMESPACES)
        if "по результатам контроля" in (text := visible_text(paragraph))
    ]
    if len(conclusions) != 1:
        raise ValueError(f"Ожидалось одно стандартное поле заключения: {path}")

    filled_fields = [sum(bool(row[index]) for row in fields) for index in range(3)]
    blank_conclusion = conclusions[0].count("☐") == 2
    code = re.search(r"К-\d{2}", path.name).group()
    return code, len(fields), *filled_fields, "пустой выбор" if blank_conclusion else "сверить", path.name


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("protocol_directory", type=Path)
    args = parser.parse_args()
    protocols = sorted(args.protocol_directory.glob("Протокол_К-??_*.docx"))
    results = [inspect_protocol(path) for path in protocols]
    expected_codes = [f"К-{number:02}" for number in range(1, 23)]
    if [row[0] for row in results] != expected_codes:
        parser.error("ожидается по одному бланку К-01–К-22")

    writer = csv.writer(sys.stdout, lineterminator="\n")
    writer.writerow(
        ["Испытание", "Строки", "Измерения", "Погрешности", "Выводы", "Заключение", "Файл"]
    )
    writer.writerows(results)


if __name__ == "__main__":
    main()
