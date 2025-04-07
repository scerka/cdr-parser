import struct
from collections import OrderedDict
from datetime import datetime

# BCD код в дату
def bcdToTime(bcdbytes):
    # к году прибавляем 2000, остальное как есть
    return datetime(2000 + bcdbytes[0], bcdbytes[1], bcdbytes[2], bcdbytes[3], bcdbytes[4], bcdbytes[5])

# BCD код в номер (не используется)
def bcdToNumber(bcdbytes):
    number = ""
    for byte in bcdbytes:
        # Разбираем байт на две тетрады
        high = (byte >> 4) & 0x0F
        low = byte & 0x0F

        # Отбрасываем 0x0F
        if high != 0x0F:
            number += str(high)
        if low != 0x0F:
            number += str(low)

    return number

# BCD код в строку
def bcdToString(bcdbytes):
    result = []
    for byte in bcdbytes:
        # Разбираем байт на две тетрады
        high = (byte >> 4) & 0x0F
        low = byte & 0x0F
        
        # Преобразуем тетрады в символы
        for nibble in [high, low]:
            # Отбрасываем 0x0F
            if nibble != 0x0F:
                # Преобразуем в символ (0-9, A-F)
                if nibble < 10:
                    result.append(str(nibble))
                else:
                    # Для значений 10-15 используем буквы A-F
                    result.append(chr(ord('а') + nibble - 10))
    
    return ''.join(result)

# Парсинг 907 байт Huawei NGN SoftX Bill формата Fixed Ordinary Detail Bill Format
def parseCDR(binaryData):
    if len(binaryData) != 907:
        raise ValueError(f"Неверная длина CDR. Ожидалось 907 байт, получено {len(binaryData)}")
        
    ulyanovskCode = '8422'

    record = OrderedDict()
    
    # ans_time, offset = 11, lenght = 6
    offset = 11
    record['ans_time'] = bcdToTime(struct.unpack_from('BBBBBB', binaryData, offset))
    
    # end_time, offset = 17, lenght = 6
    offset = 17
    record['end_time'] = bcdToTime(struct.unpack_from('BBBBBB', binaryData, offset))
    
    # conversation_time, offset = 23, lenght = 4
    offset = 23
    record['conversation_time'] = struct.unpack_from('L', binaryData, offset)[0]
    # Получаем секунды и огругляем (документация: conversation_time - unit is 10 ms)
    record['conversation_time'] = round(record['conversation_time'] * 10 / 1000)
    
    # caller_number, offset = 30, lenght = 16
    offset = 30
    lenght = 16
    record['caller_number'] = bcdToString(binaryData[offset:offset + lenght])
    
    # Если номер 6 символов, то добавляем код 8422
    if len(record['caller_number']) == 6:
        record['caller_number'] = ulyanovskCode + record['caller_number'];
    
    # called_number, offset = 49, lenght = 16
    offset = 49
    lenght = 16
    record['called_number'] = bcdToString(binaryData[offset:offset + lenght])
    
    # Если номер 6 символов, то добавляем код 8422
    if len(record['called_number']) == 6:
        record['called_number'] = ulyanovskCode + record['called_number'];
        
    # trunk_group_in, offset = 77, lenght = 2
    offset = 77
    lenght = 2
    
    # Не правильный формат
    #record['trunk_group_in'] = struct.unpack_from('>H', binaryData, offset)[0]
    
    # Если значение 0xffff то транк равен 65535, иначе преобразованное значение
    record['trunk_group_in'] = 65535 if binaryData[offset:offset + lenght].hex() == 'ffff' else int(binaryData[offset] + binaryData[offset + 1])
    
    # trunk_group_out, offset = 79, lenght = 2
    offset = 79
    lenght = 2
    
    # Не правильный формат
    #record['trunk_group_out'] = struct.unpack_from('>H', binaryData, offset)[0]
    
    # Если значение 0xffff то транк равен 65535, иначе преобразованное значение
    record['trunk_group_out'] = 65535 if binaryData[offset:offset + lenght].hex() == 'ffff' else int(binaryData[offset] + binaryData[offset + 1])
    
    # termination_code, offset = 87, lenght = 1
    offset = 87
    
    record['termination_code'] = struct.unpack_from('B', binaryData, offset)[0]
    
    # call_type, offset = 85, lenght = 0.5
    offset = 85
    
    callType = binaryData[offset]
    callType = callType & 0x0F  # Младшие 4 бита
    #callType = (callType & 0xF0) >> 4  # Cтаршие 4 бита
    
    record['call_type'] = callType

    # ENUM из документации
    enumCallType = {
        0: "unknown",
        1: "intra-office",
        2: "incoming office",
        3: "outgoing office",
        4: "tandern",
        5: "new service",
    }
    record['call_etype'] = enumCallType.get(callType, f"unknown ({callType})")
    
    # bearer_service, offset = 138, lenght = 1
    offset = 138
    
    bearerService = struct.unpack_from('B', binaryData, offset)[0]
    record['bearer_service'] = bearerService
    
    # ENUM из документации
    enumBearerService = {
        1: "circuit mode, 64Kbps unrestricted, 8KHZ structured bearer service",
        3: "circuit mode, 64Kbps, 8KHZ structured bearer 3.1KHZ voice",
        4: "packet mode, ISDN virtual call, permanent virtual circuit service is accessed by the subscriber provided by the B channel",
        5: "subscriber signaling bearer service",
        7: "circuit mode, 2X64Kbps unrestricted, 8KHZ structured bearer service type",
        8: "circuit mode, 6X64Kbps unrestricted, 8KHZ structured bearer service type",
        9: "circuit mode, 24X64Kbps unrestricted, 8KHZ structured bearer service type",
        10: "circuit mode, 30X64Kbps unrestricted, 8KHZ structured bearer service type",
        11: "subgroup voice service",
        12: "subgroup video service",
        13: "fax service",
        14: "modem service",
        100: "voice, analog subscriber calls analog subscriber",
        101: "voice, analog subscriber calls digit subscriber",
        102: "voice, digit subscriber calls analog subscriber",
        103: "voice, digit subscriber calls digit subscriber",
        255: "unknown"
    }
    record['bearer_eservice'] = enumBearerService.get(bearerService, f"unknown ({bearerService})")

    return record

# Чтение CDR файла
def readCDRFile(filename):
    with open(filename, 'rb') as file:
        records = []
        while True:
            # Читаем по 907 до конца файла
            binaryData = file.read(907)
            if not binaryData:
                break
            try:
                records.append(parseCDR(binaryData))
            except Exception as exception:
                print(f"Ошибка анализа записи CDR: {exception}")
        return records

# Точка входа
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Используйте: python huawei_parser.py <cdr_file.dat>")
        sys.exit(1)

    cdrRecords = readCDRFile(sys.argv[1])

    # ! TODO проверка caller_number и called_number на буквы [A-Z] .isdigit() и отбрасывание записей, если нужно

    for index, record in enumerate(cdrRecords):
        print(f"\Запись №{index + 1}:")
        print(f"caller_number: {record.get('caller_number', 'N/A')}")
        print(f"called_number: {record.get('called_number', 'N/A')}")
        print(f"ans_time: {record.get('ans_time', 'N/A')}")
        print(f"end_time: {record.get('end_time', 'N/A')}")
        print(f"conversation_time: {record.get('conversation_time', 'N/A')}")   
        print(f"trunk_group_in: {record.get('trunk_group_in', 'N/A')}")
        print(f"trunk_group_out: {record.get('trunk_group_out', 'N/A')}")
        print(f"termination_code: {record.get('termination_code', 'N/A')}")
        print(f"call_type: {record.get('call_type', 'N/A')}")
        print(f"call_etype: {record.get('call_etype', 'N/A')}")
        print(f"bearer_service: {record.get('bearer_service', 'N/A')}")
        print(f"bearer_eservice: {record.get('bearer_eservice', 'N/A')}")
