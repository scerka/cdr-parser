package cdr_parser;

import java.io.File;

/* 
 * CDR PARSER
 * AUTHOR: DMITRY ARTIUKHIN
 * VERSION: 1.0
 * */

public class Main {
	public static void main(String[] args) {
		 // Проверка кол-ва переданных аргументов
		 if (args.length > 0) {
			 
			 // Проверка кол-ва аргументов
			 if (args.length < 2) {
				 System.out.println("Передано неверное кол-во аргументов!");
				 System.exit(0);
			 }
			 
			 try {
				 // Считываем переданные аргументы
				 String type = args[0];
				 String file = args[1];
				 String output = null;
				 
				 if (type != null) {
					 String[] splitType = type.split("=");
					 
					 if (splitType.length == 2 && splitType[0].equals("type")) {
						 type = splitType[1];
					 } else {
						 System.out.println("Передано неправильный 1 параметр!");
						 System.exit(0);
					 }
				 } else {
					 System.out.println("Передано неправильный 1 параметр!");
					 System.exit(0);
				 }
				 
				 if (file != null) {
					 String[] splitFile = file.split("=");

					 if (splitFile.length == 2 && splitFile[0].equals("cdrfile")) {
						 file = splitFile[1];
						 
						 File f = new File(file);
						 if(!f.exists() || f.isDirectory()) { 
							 System.out.println("Указанный файл CDR не существует!");
							 System.exit(0);
						 }
					 } else {
						 System.out.println("Передано неправильный 2 параметр!");
						 System.exit(0);
					 }
				 } else {
					 System.out.println("Передано неправильный 2 параметр!");
					 System.exit(0);
				 }
				 
				 if (args.length > 2 && args[2] != null) {
					 String[] splitOutput = args[2].split("=");
					 
					 if (splitOutput.length == 2 && splitOutput[0].equals("output")) { 
						 File f = new File(splitOutput[1]);
						 
						 if (f.exists() && f.isDirectory()) {
							 output = splitOutput[1];
						 } else {
							 System.out.println("Указанная папка для выходного файла не существует!");
							 System.exit(0);
						 }
						 
					 } else {
						 System.out.println("Передано неправильный 3 параметр!");
						 System.exit(0);
					 }
				 }

				 switch(type) {
				 	case "huawei907b":
				 		Huawei.ParseCDR(file, output);
				 		break;
				 	case "eltex":
				 		Eltex.ParseCDR(file, output);
				 		break;
				 	default:
				 		System.out.println("Выбран несуществующий тип CDR!");
						System.exit(0);
				 		break;
				 }
				 
		     } catch (Exception exeption) {
		    	 System.out.println(exeption.getLocalizedMessage());
				 System.exit(0);
		     }
		 } else {
			 System.out.println("Передано неверное кол-во аргументов!");
			 System.exit(0);
		 }     
	}
}