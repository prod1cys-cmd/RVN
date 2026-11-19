# Вибрация, ориентация и тепловой режим

Запуск `python3 calculate.py` формирует `vibration.csv`, `thermal_converter_rails.csv` и `thermal_reference_points.csv`. Параметры и атрибуция исходных данных приведены в `inputs.json`. Зависимости из стандартной библиотеки Python 3.

Результаты относятся к двухимпульсному вычитателю и к расчётным режимам питания. Проверка максимума по частоте проведена на сетке 0,1 Гц. Не проводились натурные измерения, расчёт собственных частот сборки или пространственное тепловое моделирование.

## Источники

- RVN, коммит `2d8bd10eb57b32262a08e4979e4d687d8ffdbe52`. Книга 3 в каталоге `Отчетная документация`, схемы питания и тактирования АРБМ.468157.011Э2, перечень элементов АРБМ.468157.011ПЭ3, сборочный чертёж АРБМ.468157.011СБ. [Репозиторий](https://github.com/prod1cys-cmd/RVN/tree/2d8bd10eb57b32262a08e4979e4d687d8ffdbe52)
- IACS UR E10 Rev. 9, August 2023, п. 7. [Текст](https://iacs.s3.af-south-1.amazonaws.com/wp-content/uploads/2022/02/19142351/UR-E10-Rev.9-Aug-2023-UL.pdf)
- FURUNO. Installation Manual, Marine Radar FAR-2xx8 and FAR-2018/2028-MARK-2, IME-36520-X, 14.11.2024, §§ 1.1, 1.6, 1.10, 2.2. SHA-256 PDF `5f382eb93386a9a21ab09eaf48e7f0570f61487cf8d759e0a3fea8f0f2bc0977`. [Руководство](https://furuno.ru/wp-content/uploads/2025/02/far20x8mk2_installation_manual.pdf)
- Analog Devices. HMC7044 data sheet Rev. E, таблица 2. [Документация](https://www.analog.com/media/en/technical-documentation/data-sheets/hmc7044.pdf)
- Analog Devices. AD8367 data sheet, таблица 1. [Документация](https://www.analog.com/media/en/technical-documentation/data-sheets/AD8367.pdf)
- AMD. DS191, рабочая температура перехода промышленной градации. [Документация](https://docs.amd.com/v/u/en-US/ds191-XC7Z030-XC7Z045-data-sheet)
- STMicroelectronics. STM32H745xI/G data sheet DS12923, таблицы потребления в Run. [Документация](https://www.st.com/resource/en/datasheet/stm32h745xi.pdf)

## Открытые данные

- Подтверждённая конфигурация HMC7044, механическая передаточная функция крепления, виброчувствительность генераторов по осям, измерения боковых полос с разных ступеней тракта.
- Первичная документация К5119ПВ1Я, потребление действующей конфигурации преобразователя, отчёты о мощности XC7Z030 для обеих сборок, режимы работы STM32, памяти и коммутатора, замеры по отдельным шинам.
- Модель корпуса, контактов теплоотвода, системы крепления и воздушных каналов, состояние вентиляторов, параметры и требования режима отказа, результаты температурных измерений.
