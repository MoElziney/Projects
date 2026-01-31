package com.mycompany.company;


/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */



import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.Scanner;



/**
 *
 * @author MoazE
 */
public class Passenger {
    private String name ;
    private String password;
    private int id ;
    private String email;
    private ArrayList<Booking> passengerBookings;
    private ArrayList<Passenger> passengerData=new ArrayList<>();

    Scanner input= new Scanner(System.in);
    
    
    public Passenger (){
        name=" ";
        id=0;
        email=" ";
passengerData.add(new Passenger("moaz","535","Moaz@"));


    } 
    public Passenger(String name, String password, String email) {
        this.name = name;
        this.password=password;
        this.id = (int) (Math.random() * 900);
        this.email = email;
       
    }
    
   

    

    public String getName() {
        return name;
    }
   

    @Override
    public String toString() {
        return "Passenger{" + "name=" + name + ", id=" + id + ", email=" + email + '}';
    }
    

    public void setName(String name) {
        this.name = name;
    }

    public int getId() {
        return id;
    }

    public String getPassword() {
        return password;
    }

    public void setPassword(String password) {
        this.password = password;
    }

    public void setId(int id) {
        this.id = id;
    }

    public void setPassengerBookings(ArrayList<Booking> passengerBookings) {
        this.passengerBookings = passengerBookings;
    }

    public ArrayList<Passenger> getPassengerData() {
        return passengerData;
    }

   
    
     
    public String getEmail() {
        return email;
    }

    public void setEmail(String email) {
        this.email = email;
    }

    public ArrayList<Booking> getPassengerBookings() {
        return passengerBookings;
    }

    
    
  

    
    public void createAccount(Passenger m){
       passengerData.add(m);
    }
    
     public  Boolean searchAccount (String mail){
      
 Boolean check=false;
      for (int i=0; i<passengerData.size();i++){
           check= false ;
          if (passengerData.get(i).getEmail().equals(mail) ){
           check=true ;
           break;
          }
    

     }
      return check ;
     }
            
     public void  manageAccount  (String name,String email ,String pass){
        
          this.name=name;
          this.email=email;
          this.password=pass;
             
          
          
                   }
// booking a tichet 
    public void bookATicket(String bookingDate, int numberOfPassengers,  String departureAirport
            ,String destinationAirport, String departureDate,int id ,String arrivalDate){
          
         ArrayList <Booking>Bookings=passengerBookings;
        
          Booking b1 = new Booking (bookingDate,numberOfPassengers,departureAirport
                  ,destinationAirport,departureDate, id,arrivalDate);
          Bookings.add(b1);
          
          }
  // overload of the booking a ticket   
    public void bookATicket(Booking b){
       ArrayList <Booking>Bookings=passengerBookings;
          Bookings.add(b);
          }


    // search the book by booking id
 
    
    public Boolean searchBook(int id){
        
        Boolean check=false;
    for(int i =0;i<passengerBookings.size();i++){
        if(passengerBookings.get(i).getBookingId() == id){
            check=true;
        break;
    }
    }
    return check;
    }
    // get the booking by the id
    public Booking findBook(int cancelID){
          
        Booking B=new Booking ();
    if(searchBook(cancelID)){
    for(int i =0;i<passengerBookings.size();i++){
        if(passengerBookings.get(i).getBookingId()==cancelID){
            B= passengerBookings.get(i);
    
    }
    }
    }else{
    System.out.print("this ID is not exist");
    }
    return B;
    }
    // cancel the booking by the id
    public void cancelBook(Booking cancelBooking ){
         
        if(searchBook(cancelBooking.getBookingId())){
    for(int i=0;i<passengerBookings.size();i++){
    if(passengerBookings.get(i).getBookingId()==cancelBooking.getBookingId()){
        
        Booking bRemove=passengerBookings.get(i);
        
        bRemove.returnSeats(bRemove.getBookingSeatId());
        
            passengerBookings.remove(i);
    
    }
    
    }
      
        }else System.out.println("this booking is not exist");
    }
    
    public void updateBooking(Booking oldBooking, Booking newBooking) {
         if(searchBook(oldBooking.getBookingId())){
    for (int i = 0; i < passengerBookings.size(); i++) {
        if (passengerBookings.get(i).getBookingId() == oldBooking.getBookingId()) {

            cancelBook(oldBooking);

// appear the interface of add new booking
            bookATicket(newBooking);
            
                    
    }
    

    
    }
}else System.out.println("this booking is not exist");
    }
    
    public  Passenger verifyAccount (String email, String password ,ArrayList <Passenger>passengerData){
      ArrayList <Passenger>listOfPassengers=passengerData;
 Boolean check=false;
      for (int i=0; i<listOfPassengers.size();i++){
           check= false ;
          if (listOfPassengers.get(i).getEmail().equals(email) && listOfPassengers.get(i).getPassword().equals(password) ){
           return listOfPassengers.get(i);
           
          }
    

     }
      return null ;
     }
    // view the booking list of the passenger
    public void Viewlist(int passId){
      ArrayList <Booking>Bookings=passengerBookings;
    for(int i=0; i<Bookings.size();i++){
    if(Bookings.get(i).getPassengerID()== passId){
    System.out.print(Bookings.get(i));
    }
    
    }
    }
    
    public void printPassengerList(){
    
    String filePath = "PassengerList.txt";

        try {
            // Creating a FileWriter object
            FileWriter fileWriter = new FileWriter(filePath);

            // Creating a PrintWriter object
            PrintWriter printWriter = new PrintWriter(fileWriter);

            // Looping through the array and writing each string to the file
            for (int i=0;i<getPassengerData().size();i++) {
                String str=getPassengerData().get(i).toString();
                printWriter.println(str);
            }

            // Closing the PrintWriter
            printWriter.close();

            System.out.println("Strings have been written to the file successfully.");

        } catch (IOException e) {
            System.out.println("An error occurred while writing to the file: " + e.getMessage());
        }
    }
    
    public void printPassengerBookingList(){
    
    String filePath = "PassengerBookingList.txt";

        try {
            // Creating a FileWriter object
            FileWriter fileWriter = new FileWriter(filePath);

            // Creating a PrintWriter object
            PrintWriter printWriter = new PrintWriter(fileWriter);

            // Looping through the array and writing each string to the file
            for (int i=0;i<getPassengerBookings().size();i++) {
                String str=getPassengerBookings().get(i).toString();
                printWriter.println(str);
            }

            // Closing the PrintWriter
            printWriter.close();

            System.out.println("Strings have been written to the file successfully.");

        } catch (IOException e) {
            System.out.println("An error occurred while writing to the file: " + e.getMessage());
        }
    }
    
    
    }//end


    
    
   
    
    
   

