/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
package Resources;

/**
 *
 * @author Mohamed Khaled
 */


import Classes.TShirt;
import java.net.*;
import java.io.*;
import java.util.ArrayList;

public class Resource1 implements Runnable {
    
    Socket process;
   public static ArrayList<TShirt> Tshirts = new ArrayList<TShirt>();
   public static int count;
    
   
    public Resource1(Socket process) {
        this.process = process;
        
        produceProducts();
        run();
        
        
        
}
    
    
     @Override
    public void run() {
        try {
            
            ObjectOutputStream output = new ObjectOutputStream(process.getOutputStream());
            ObjectInputStream input = new ObjectInputStream(process.getInputStream());
            
            TShirt selected = (TShirt) input.readObject();
            if(retreiveItem(selected)){
                System.out.println(selected.toString());
            output.writeObject(selected);
            
            output.flush();
            }
            else{
                String notfound = "The product does not exist";
                output.writeObject(notfound);
            output.flush();
            }
            process.close();
            input.close();
            output.close();
        } catch (Exception e) {
            System.out.println(e);
        }
    }
    
    public static void produceProducts() {
        Tshirts.add(new TShirt("M","Red","Cotton"));
            Tshirts.add(new TShirt("L","grey","Polyster"));
            Tshirts.add(new TShirt("S","White","COtton"));
}
    public boolean retreiveItem(TShirt selected){
        for(TShirt t :Tshirts){
            
            if(t.equals(selected)){
            Tshirts.remove(t);
                return true;
            }
            
        }
       return false;
    }
    
    
    public void display(){
    
        for(int i = 0; i< Tshirts.size();i++){
            System.out.println(Tshirts.get(i).toString());
        }
    }
    public static void main(String[] args) {
        try{
            
            ServerSocket resource = new ServerSocket(2000);
            System.out.println("Listening");
            while (true) {
                Socket clientSocket = resource.accept();
                System.out.println ("Connected");
                Thread Client = new Thread(new Resource1(clientSocket));
                Client.start();
            
            }
            
        }catch(Exception e){
            System.out.println(e);
        }
    }
    
}

