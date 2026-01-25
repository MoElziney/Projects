/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
package Processes;

import Classes.TShirt;
import java.io.*;
import java.net.Socket;
import java.util.Scanner;

/**
 *
 * @author Mohamed Khaled
 */
public class Client1 {
    
    
     public static void main(String args[]) {
        try {
            Socket s1 = new Socket("localhost", 3000);
            ObjectOutputStream output = new ObjectOutputStream(s1.getOutputStream());
            ObjectInputStream input = new ObjectInputStream(s1.getInputStream());
            Scanner sc = new Scanner(System.in);
            System.out.println("enter ip:");
            int ip = sc.nextInt();
           TShirt x; //new TShirt("M","Red","Cotton")
           x = new TShirt("M","Red","Cotton");
           String s = "ssss";
//            output.writeInt(ip);
//            output.flush();
            output.writeObject(x);
            output.flush();
            TShirt msg = (TShirt)input.readObject();
            System.out.println(msg.toString());
            input.close();
            output.close();
            s1.close();
        
        } catch (Exception e) {
            System.out.println(e);
        }
    }
}
