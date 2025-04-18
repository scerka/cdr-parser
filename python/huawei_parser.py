import struct
from collections import OrderedDict
from datetime import datetime

# Байты в дату
def bytesToTime(datebytes):
    # к году прибавляем 2000, остальное как есть
    return datetime(2000 + datebytes[0], datebytes[1], datebytes[2], datebytes[3], datebytes[4], datebytes[5])

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
    
    # answer_flag, offset = 171.375, lenght = 0.125, unsigned char
    offset = 171
    bitOffset = 3
    
    record['answer_flag'] = (binaryData[offset] >> bitOffset) & 0x01
    
    record['answer_flag_text'] = 'answer' if record['answer_flag'] == 0 else 'no answer'
    
    # ans_time, offset = 11, lenght = 6, unsigned char
    offset = 11
    record['ans_time'] = bytesToTime(struct.unpack_from('BBBBBB', binaryData, offset))
    
    # end_time, offset = 17, lenght = 6, unsigned char
    offset = 17
    record['end_time'] = bytesToTime(struct.unpack_from('BBBBBB', binaryData, offset))
    
    # conversation_time, offset = 23, lenght = 4, unsigned long (unit is 10 ms)
    offset = 23
    record['conversation_time'] = round(struct.unpack_from('<L', binaryData, offset)[0] * 0.01)
    
    # caller_number, offset = 30, lenght = 16, BCD
    offset = 30
    lenght = 16
    record['caller_number'] = bcdToString(binaryData[offset:offset + lenght])
    
    # Если номер 6 символов, то добавляем код 8422
    if len(record['caller_number']) == 6:
        record['caller_number'] = ulyanovskCode + record['caller_number'];
    
    # called_number, offset = 49, lenght = 16, BCD
    offset = 49
    lenght = 16
    record['called_number'] = bcdToString(binaryData[offset:offset + lenght])
    
    # Если номер 6 символов, то добавляем код 8422
    if len(record['called_number']) == 6:
        record['called_number'] = ulyanovskCode + record['called_number'];
        
    # trunk_group_in, offset = 77, lenght = 2, unsigned short
    offset = 77
    lenght = 2
    
    # Если значение 0xffff то транк равен 65535, иначе преобразованное значение
    record['trunk_group_in'] = 65535 if binaryData[offset:offset + lenght].hex() == 'ffff' else struct.unpack_from('<H', binaryData, offset)[0]
    
    # trunk_group_out, offset = 79, lenght = 2, unsigned short
    offset = 79
    lenght = 2
    
    # Если значение 0xffff то транк равен 65535, иначе преобразованное значение
    record['trunk_group_out'] = 65535 if binaryData[offset:offset + lenght].hex() == 'ffff' else struct.unpack_from('<H', binaryData, offset)[0]
    
    # termination_code, offset = 87, lenght = 1, unsigned char
    offset = 87
    
    record['termination_code'] = struct.unpack_from('B', binaryData, offset)[0]
    
    # call_type, offset = 85, lenght = 0.5, unsigned char
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
    
    # bearer_service, offset = 138, lenght = 1, unsigned char
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

    records = readCDRFile(sys.argv[1])

    for index, record in enumerate(records):
        print(f"\nЗапись №{index + 1}:")
        print(f"answer_flag: {record.get('answer_flag', 'N/A')}")
        print(f"answer_flag_text: {record.get('answer_flag_text', 'N/A')}")
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
