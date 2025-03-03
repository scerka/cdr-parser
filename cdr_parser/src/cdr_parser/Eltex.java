package cdr_parser;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;

/*
 * PARSER ELTEX
 * Based on the parser eltex_smg_2016 from Inline Telecom Solutions (ASR Bill-Master 11.0.0)
 * */

public class Eltex {
	 public static void ParseCDR(String file, String output) {
		 try {
			 File f = new File(file);
			 if (!f.getName().endsWith(".cdr")) {
				 System.out.println("Для CDR типа eltex, расширение файла должно быть .cdr!");
				 System.exit(0);
			 }
			 
			 FileWriter fileWriter;
				
			 if (output != null) {
				output = output + File.separator + f.getName() + ".csv";
					
				fileWriter = new FileWriter(output);
			} else {
				fileWriter = new FileWriter(file.toString() + ".csv");
			}
				
	        PrintWriter printWriter = new PrintWriter(fileWriter);
	        printWriter.println("type_cdr;answer_flag;caller_number;called_number;ans_time;end_time;conversation_time;trunk_group_in;trunk_group_out;termination_code;bearer_service");
			 
			 FileReader fileReader = new FileReader(file);
			 BufferedReader bufferedReader = new BufferedReader(fileReader);
			 String line = bufferedReader.readLine();

			 while (line != null) {
				 if (!line.startsWith("Eltex;")) {
					 continue;
				 }
				 
				 String[] lines = line.split(";");
				 
				 String type = "Eltex";
				 String aNumber = lines[11];
				 String bNumber = lines[23];
				 String callStart = convertDate(lines[1]);
				 String callStop = convertDate(lines[27]);
				 String callDuration = lines[2];
				 String code = lines[3] + "/" + lines[4];
				 String trunkIn = lines[7];
				 String trunkOut = lines[18];
				 String redirFlag = lines[13];
				 String answerFlag = Integer.parseInt(callDuration) > 0 ? "ANSWER" : "NO_ANSWER";
				 
				 if (bNumber == "") bNumber = lines[22];
				 
				 // if it is internal call, then use another fields for IN/OUT trunks
				 String regex = "^\\d+$";
				 
				 if (trunkIn.matches(regex)) {
					 trunkIn = lines[6];
				 }
				 
				 if (trunkOut.matches(regex)) {
					 trunkOut = lines[17];
				 }
				 
				 // it is two cdr lines for redirected call, use another fields for A/B-numbers
				 if (redirFlag.matches("redirecting")) {
					 aNumber = lines[14];
				 }
				 
				 if (redirFlag.matches("redirected")) {
					 bNumber = lines[22];
				 }
				 
				 printWriter.println(type + ";" + answerFlag + ";" + aNumber + ";" + bNumber + ";" + callStart + ";" + callStop + ";" + callDuration + ";" + trunkIn + ";" + trunkOut + ";" + code + ";" + "");
				 
				 line = bufferedReader.readLine();
			 }

			 bufferedReader.close();
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
	 
	 // конвертация даты
	 private static String convertDate(String date) {
		 String[] splitDate = date.split(" ");
		 String[] dateArray = splitDate[0].split("-");
		  
		return dateArray[2] + "." + dateArray[1] + "." + dateArray[0] + " " + splitDate[1]; 

	 }
}