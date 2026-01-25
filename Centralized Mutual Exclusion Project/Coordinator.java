/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
package Coordinator;

/**
 *
 * @author Mohamed Khaled
 */

import Classes.TShirt;
import java.net.*;
import java.io.*;

public class Coordinator implements Runnable {
    
    Socket process;

    public Coordinator(Socket process) {
        this.process = process;
    }
    
    
    @Override
    public void run() {
        try{
            //server side
        ObjectOutputStream clientOutput = new ObjectOutputStream(process.getOutputStream());
        ObjectInputStream clientInput = new ObjectInputStream(process.getInputStream());
//           int data = clientInput.readInt();
//         System.out.println(data);
            String s = clientInput.readUTF();
           // System.out.println(s.toString());
        //client side
        Socket client = new Socket("Localhost",2000);
        ObjectOutputStream output = new ObjectOutputStream(client.getOutputStream());
         ObjectInputStream input = new ObjectInputStream(client.getInputStream());
        // String m = "2017"; 
        //output.writeObject(m);
        output.writeUTF(s);
        output.flush();
        
        String msg = input.readUTF();
        
        clientOutput.writeUTF(msg);
        clientOutput.flush();
        
        process.close();
        client.close();
        clientInput.close();
        clientOutput.close();
        input.close();
        output.close();
        
    }catch(Exception e){
            System.out.println(e);
    }
    }
    
    public static void main(String[] args) {
        try{
            ServerSocket Resource = new ServerSocket(3000);
            System.out.println("Listenning");
            while(true){
                Socket client = Resource.accept();
                System.out.println("connected");
                Thread t = new Thread(new Coordinator(client));
                t.start();
            }
        }catch(Exception e){
            System.out.println(e);
    }
  }
    
}
