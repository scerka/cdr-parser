# CDR PARSER
Парсинг call detail record (CDR) файлов.

Программа написана на языке **Java**.

## Требования для запуска
Java Development Kit (JDK) версии **23 и выше**.\
[OpenJDK](https://openjdk.org/), [Microsoft Build of OpenJDK](https://www.microsoft.com/openjdk)

## Аргументы для запуска
1. type - тип CDR файла, доступно 2 значения **huawei907b** и **eltex**. [Обязателный]
2. cdrfile - полный путь до CDR файла. [Обязательный]
3. output - путь в который положиться выходной csv файл. [Необязательный]

*Указывать аргументы нужно в строгом порядке, как написано выше.*

## Примеры

Парсинг CDR файлов HUAWEI - NGN SoftX Bill iGWB CDR Format 907 Bytes Binary
```
java -jar cdr_parser.jar type=huawei907b cdrfile=b01015983.dat
```

Парсинг CDR файлов Eltex
```
java -jar cdr_parser.jar type=eltex cdrfile=20250212091745.cdr
```

Пример с указание аргемента **output**
```
java -jar cdr_parser.jar type=huawei907b cdrfile=/var/www/b01015983.dat output=/var/www/huawei/
```

## HUAWEI - NGN SoftX Bill iGWB CDR Format 907 Bytes Binary

```
1. ans_time, offset = 11, lenght = 6
2. end_time, offset = 17, lenght = 6
3. conversation_time, offset = 23, lenght = 4
4. trunk_group_in, offset = 77, lenght = 2
5. trunk_group_out, offset = 79, lenght = 2
6. caller_number, offset = 30, lenght = 16
7. called_number, offset = 49, lenght = 16
8. termination_code, offset = 87, lenght = 1
9. bearer_service, offset = 138, lenght = 1
```
