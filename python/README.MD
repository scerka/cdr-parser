# CDR PARSER
Парсинг call detail record (CDR) файлов.

Программа написана на языке **Python**.

## Требования для запуска
Python версии **3 и выше**.\
[Python](https://www.python.org/)

## Аргументы для запуска
1. cdrfile - полный путь до CDR файла. [Обязательный]

## Примеры

```
python huawei_parser.py b01015983.dat
```

## HUAWEI - NGN SoftX Bill iGWB CDR Format 907 Bytes Binary

```
1. ans_time, offset = 11, lenght = 6, unsigned char
2. end_time, offset = 17, lenght = 6, unsigned char
3. conversation_time, offset = 23, lenght = 4, unsigned long
4. caller_number, offset = 30, lenght = 16, BCD
5. called_number, offset = 49, lenght = 16, BCD
6. trunk_group_in, offset = 77, lenght = 2, unsigned short
7. trunk_group_out, offset = 79, lenght = 2, unsigned short
8. call_type, offset = 85, lenght = 0.5, unsigned char
9. termination_code, offset = 87, lenght = 1, unsigned char
10. bearer_service, offset = 138, lenght = 1, unsigned char
11. answer_flag, offset = 171.375, lenght = 0.125, unsigned char
```
