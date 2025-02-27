package cdr_parser;

import java.io.DataInputStream;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;
import java.io.File;

/*
 * PARSER HUAWEI - NGN SoftX Bill iGWB CDR Format 907 Bytes Binary
 * */

public class Huawei {
	 public static void ParseCDR(String file, String output) {
		try {
			File f = new File(file);
			
			if (!f.getName().endsWith(".dat")) {
				System.out.println("Для CDR типа huawei907b, расширение файла должно быть .dat!");
				System.exit(0);
			}
			
			FileInputStream fileInputStream = new FileInputStream(file);
			DataInputStream dataInputStream = new DataInputStream(fileInputStream);
			
			FileWriter fileWriter;
			
			if (output != null) {
				output = output + File.separator + f.getName() + ".csv";
				
				fileWriter = new FileWriter(output);
			} else {
				fileWriter = new FileWriter(file.toString() + ".csv");
			}
			
            PrintWriter printWriter = new PrintWriter(fileWriter);
            
            printWriter.println("type_cdr;answer_flag;caller_number;called_number;ans_time;end_time;conversation_time;trunk_group_in;trunk_group_out;termination_code;bearer_service");
            
            while (dataInputStream.available() != 0) {
            	byte[] bytes = new byte[907 + 1];
            	
            	 for (int i = 1; i <= 907; i++) {
            		 bytes[i] = dataInputStream.readByte();
            	 }
            	
            	// type_cdr
            	String type = "HUAWEI - NGN SoftX Bill iGWB CDR Format 907 Bytes Binary";
            	
            	// ans_time, offset = 11, lenght = 6
            	String answerTime = getDate(bytes, 11);
            	// end_time, offset = 17, lenght = 6
            	String endTime = getDate(bytes, 17);
            	// conversation_time, offset = 23, lenght = 4
            	String conversationTime = getTime(bytes, 23);
            	
            	// answer_flag, logic (not parse cdr)
            	String answerFlag = Integer.parseInt(conversationTime) > 0 ? "ANSWER" : "NO_ANSWER";
            	
            	// trunk_group_in, offset = 77, lenght = 2
            	String trunkGroupIn = getTrunk(bytes[78], bytes[79]);
            	// trunk_group_out, offset = 79, lenght = 2
            	String trunkGroupOut = getTrunk(bytes[80], bytes[81]);
            	
            	// caller_number, offset = 30, lenght = 16
            	String callerNumber = getNumber(bytes, 30);
            	// called_number, offset = 49, lenght = 16
            	String calledNumber = getNumber(bytes, 49);
            	
            	// termination_code, offset = 87, lenght = 1
            	int terminationCodeByte = bytes[87 + 1];
            	
            	if (terminationCodeByte < 0) {
            		terminationCodeByte += 256;
                }
            	
            	String terminationCode = Integer.toString(terminationCodeByte);
                
            	// bearer_service, offset = 138, lenght = 1
            	String bearerService = Integer.toString(bytes[138 + 1]);
	
            	printWriter.println(type + ";" + answerFlag + ";" + callerNumber + ";" + calledNumber + ";" + answerTime + ";" + endTime + ";" + conversationTime + ";" + trunkGroupIn + ";" + trunkGroupOut + ";" + terminationCode + ";" + bearerService);
            }
            
            fileInputStream.close();
            printWriter.close();
            
		} catch (FileNotFoundException e) {
			System.out.println(e.getLocalizedMessage());
			System.exit(0);
		} catch (IOException e) {
			System.out.println(e.getLocalizedMessage());
			System.exit(0);
		}
		System.out.println("OK");
		System.exit(0);
	 }
	 
	 private static String getTime(byte[] bytes, int offset) {
		 String binary = decimalToBinary(bytes[offset + 1]);
		 binary = decimalToBinary(bytes[offset + 2]) + binary;
		 binary = decimalToBinary(bytes[offset + 3]) + binary;
         binary = decimalToBinary(bytes[offset + 4]) + binary;
         
         double exp = 0, duration = 0;

         for (int i= binary.length(); i > 0; i--) {
             int bit = Integer.parseInt(Character.toString(binary.charAt(i - 1)));

             duration = duration + bit * Math.pow(2.0, exp);

             exp += 1;
         }

         duration = Math.round(duration / 100);
		 
		 return Integer.toString((int)duration);
	 }
	 
	 // получение телефона
	 private static String getNumber(byte[] bytes, int offset) {
		 String number = "";
		 boolean flag = false;
		 
		 byte[] phoneBytes = new byte[16];
		 
		 for (int i = 1; i <= 16; i++) {
			 if (flag) {
				 break;
			 }
			 
			 phoneBytes[i - 1] = bytes[offset + i];
			 
			 // Старый способ
			 /*byte b = bytes[offset + i];
             String binary = decimalToBinary(b);

             test += binary;
             
             int first4 = binaryToDecimal(binary.substring(0, 4));
             int last4 = binaryToDecimal(binary.substring(4));

             String first4hex = decimalToHex(first4);
             String last4hex = decimalToHex(last4);

             if (first4hex == "F") {
            	 flag = true;
             } else {
            	 number = number + first4hex;
             }

             if (last4hex == "F") {
            	 flag = true;
             } else {
            	 number = number + last4hex;
             }*/
		 }
		 
		 number = bcdToString(phoneBytes, 0, 16, false);
		 
		 return number;
	 }
	 
	 // получение транка
	 private static String getTrunk(byte first, byte second) {
		 String binary = decimalToBinary(first);
		 binary = decimalToBinary(second) + binary;

		 return Integer.toString(binaryToDecimal(binary));
	 }
	 
	 // получение даты
	 private static String getDate(byte[] bytes, int offset) {
		 int year = 2000 + bytes[offset + 1];
		 int month = bytes[offset + 2];
		 int day = bytes[offset + 3];
		 
		 int hour = bytes[offset + 4];
		 int munutes = bytes[offset + 5];
		 int seconds = bytes[offset + 6];
		 
		 String stringYear = Integer.toString(year);
		 String stringMonth = Integer.toString(month);
		 String stringDay = Integer.toString(day);
		 String stringHour = Integer.toString(hour);
		 String stringMinutes = Integer.toString(munutes);
		 String stringSeconds = Integer.toString(seconds);	 
		 
		 if (month < 10) stringMonth = "0" + stringMonth;
		 if (day < 10) stringDay = "0" + stringDay;
		 if (hour < 10) stringHour = "0" + stringHour;
		 if (munutes < 10) stringMinutes = "0" + stringMinutes;
		 if (seconds < 10) stringSeconds = "0" + stringSeconds;
		 
		 return stringDay + "." + stringMonth + "." + stringYear + " " + stringHour + ":" + stringMinutes + ":" + stringSeconds;
	 }
	 
	 // десятичное в бинарное
	 private static String decimalToBinary(int decimal) {
		 if (decimal < 0) {
			 decimal += 256;
		 }

		 String output = Integer.toBinaryString(decimal);
		 for (int i = output.length(); i < 8; i++) {
			 output = "0" + output;
		 }

		 return output;
	}
	
	// десятичное в хекс
	 private static String decimalToHex(int decimal) {
        if (decimal < 0) {
        	decimal += 256;
        }

        String output = Integer.toString(decimal);

        if (output.equals("10"))
            return "A";
        else if (output.equals("11"))
        	output = "B";
        else if (output.equals("12"))
        	output = "C";
        else if (output.equals("13"))
        	output = "D";
        else if (output.equals("14"))
        	output = "E";
        else if (output.equals("15"))
        	output = "F";

        return output;
	}
    
    // бинарное в десятичное
	 private static int binaryToDecimal(String bin) {
		int bit, length;
		double exp = 0, num = 0;

		length = bin.length();
		for (int i = length; i > 0; i--) {
			bit = Integer.parseInt(Character.toString(bin.charAt(i - 1)));
			num = num + bit * Math.pow(2.0, exp);
			exp += 1;
		}

		return (int)num;
	}
	 
	// bcd в строку
	public static String bcdToString(byte[] b, int offset, int len, boolean padLeft) {
		StringBuffer d = new StringBuffer(len);
		int start = (((len & 1) == 1) && padLeft) ? 1 : 0;
		for (int i = start; i < len + start; i++) {
			int shift = ((i & 1) == 1 ? 0 : 4);
			char c = Character.forDigit(((b[offset + (i >> 1)] >> shift) & 0x0F), 16);
			
			if (c == 'd') {
				c = '=';
			}

			if (c != 'f') {
				d.append(Character.toUpperCase(c));
			}
		}
	        
		return d.toString();
	}
}