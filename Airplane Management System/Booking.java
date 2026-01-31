
package com.mycompany.company;
import java.io.*;
import java.util.ArrayList;

import java.time.LocalDateTime;

import java.util.*;

public class Booking {
   // Attributes
  
    private String bookingDate;
    private int numberOfPassengers;
    private ArrayList<Integer>bookingSeatId;
    protected Travel travel=new Travel();
    private int bookingId;
    private int passengerID;
    private String DepartureAirport;
    private String DestinationAirport;
    private String DepartureDate;
    private String ArrivalDate;
    private int price;
    private static ArrayList<Travel> bookedTravels;
    private String classDegree;
    Scanner input= new Scanner(System.in);

    
 
    //constractors
    //Default constractor

    public Booking() {
       
        this.bookingDate = null;
        this.numberOfPassengers =0;
        this.bookingSeatId = new ArrayList<>();
        this.travel = new Travel();
        this.bookingId =0;
        DepartureAirport = "JFK";
        DestinationAirport = "LAX";
        DepartureDate=  null;
        ArrivalDate =  null;
        }
   

     //Parmitarized cinstractor

 
      public Booking(String bookingDate, int numberOfPassengers, int bookingSeatId, int bookingId) {
        this.bookingDate = bookingDate;
        this.numberOfPassengers = numberOfPassengers;
        //this.bookingSeatId =  bookingSeat(numberOfPassengers);
        this.travel = new Travel();
        this.bookingId = bookingId;
        

    }

       public Booking(LocalDateTime bookingDate, int numberOfPassengers ){
        this.numberOfPassengers = numberOfPassengers;
        //this.bookingSeatId =  bookingSeat(numberOfPassengers);
        this.bookingId = (int)Math.random()*1000;
        
        
       

    }
       //bookingDate,numberOfPassengers,bookingSeatId,bookingId,departureAirport,destinationAirport,departureDate1,arrivalDate1
    public Booking(String bookingDate, int numberOfPassengers,  String departureAirport
            , String destinationAirport, String departureDate, int passengerID, String arrivalDate) {
        this.bookingDate = bookingDate;
        this.numberOfPassengers = numberOfPassengers;
        //this.bookingSeatId =  bookingSeat(numberOfPassengers);
        this.bookingId = (int)(Math.random()*1000);
        this.setDepartureAirport(departureAirport);
        this.setDestinationAirport(destinationAirport);
        this.setDepartureDate(departureDate);
        this.setArrivalDate(arrivalDate);
        this.passengerID=passengerID;
        this.travel=new Travel();

    }
public Booking(String bookingDate, int numberOfPassengers, int[] bookingSeatId, int bookingId, 
            int passengerID, String DepartureAirport, String DestinationAirport,
            String DepartureDate, String ArrivalDate, String classDegree, int price) {
        this.bookingDate = bookingDate;
        this.numberOfPassengers = numberOfPassengers;
        //this.bookingSeatId = bookingSeatId;
        this.bookingId = bookingId;
        this.passengerID = passengerID;
        this.DepartureAirport = DepartureAirport;
        this.DestinationAirport = DestinationAirport;
        this.DepartureDate = DepartureDate;
        this.ArrivalDate = ArrivalDate;
        this.classDegree = classDegree;
        this.price = price;
    }

    public Booking(String bookingDate, int numberOfPassengers, Travel travel, String departureAirport
            , String destinationAirport, Calendar departureDate, Calendar arrivalDate, int arrivalTime, int departureTime, Flight flight, int price) {
        this.bookingDate = bookingDate;
        this.numberOfPassengers = numberOfPassengers;
        //this.bookingSeatId = bookingSeat(numberOfPassengers);
        this.travel=travel;
        this.bookingId = (int)(Math.random()*1000);
        
        
        
    }
    
// get a travel from it sn
   public void searchForTravel(int sn){
       
        boolean check=false;
        Travel checkTravel=new Travel();
       for(int i=0;i<bookedTravels.size();i++){
           check=false;
          checkTravel=bookedTravels.get(i);
          
        if(checkTravel.getTravelSerialNumber()==sn){
        check=true;
        }
       }
       if(check)
           this.travel=checkTravel;
       else {
           System.out.print("this travel is not exist");
           
           
       }
        
       
   }

  
   //Setters
    
    public void setBookingId() {
        this.bookingId = (int)(Math.random()*1000);
    }

    public void setBookingDate(String bookingDate) {
        this.bookingDate = bookingDate;
    }

    public void setNumberOfPassengers(int numberOfPassengers) {
        this.numberOfPassengers = numberOfPassengers;
    }

    public void setTravel(Travel travel) {
        this.travel = travel;
    }

    public void setBookingSeatId(ArrayList<Integer> bookingSeatId) {
        this.bookingSeatId = bookingSeatId;
    }

    public void setPassengerID(int passengerID) {
        this.passengerID = passengerID;
    }

    public void setDepartureAirport(String DepartureAirport) {
        this.DepartureAirport = DepartureAirport;
    }

    
    public void setDestinationAirport(String DestinationAirport) {
        this.DestinationAirport = DestinationAirport;
    }

    

    public void setDepartureDate(String DepartureDate) {
        this.DepartureDate = DepartureDate;
    }

  

    public void setArrivalDate(String ArrivalDate) {
        this.ArrivalDate = ArrivalDate;
    }

    public ArrayList<Travel> getBookedTravels() {
        return bookedTravels;
    }

    public void setBookedTravels(ArrayList<Travel> bookedTravels) {
        this.bookedTravels = bookedTravels;
    }

    

    

    public void setClassDegree(String classDegree) {
        this.classDegree = classDegree;
    }

   
    
    
//Getters

  

    public String getBookingDate() {
        return bookingDate;
    }

    public int getNumberOfPassengers() {
        return numberOfPassengers;
    }

    public Travel getTravel() {
        return travel;
    }
    

    public ArrayList<Integer> getBookingSeatId() {
        return bookingSeatId;
    }

    public int getBookingId() {
        return bookingId;
    }

    public int getPassengerID() {
        return passengerID;
    }

    public String getDepartureAirport() {
        return DepartureAirport;
    }
    
    public String getDestinationAirport() {
        return DestinationAirport;
    }

    public String getDepartureDate() {
        return DepartureDate;
    }
  
    
      public String getArrivalDate() {
        return ArrivalDate;
    }
      
    //to_string function

    public String getClassDegree() {
        return classDegree;
    }
 

 
    //Class functions
    //this function to display the booking details
    
      public void displayBookingDetails() {
    System.out.println("Booking Date: " + bookingDate);
    System.out.println("Number of Passengers: " + numberOfPassengers);
    System.out.println("Booking Seat ID: " + bookingSeatId);
    System.out.println("Booking ID: " + bookingId);
    System.out.println("Passenger ID: " + passengerID);
    System.out.println("Departure Airport: " + DepartureAirport);
    System.out.println("Destination Airport: " + DestinationAirport);
    System.out.println("Departure Date: " + DepartureDate);
    System.out.println("Arrival Date: " + ArrivalDate);
    System.out.println("Travel Details:");
    travel.displayTravelDetails();
}

      // calculation the booking fare
    public int calculateBooking(){
    
    return price*numberOfPassengers;
    };  
      
 

    @Override
    public String toString() {
        return "Booking{" + "bookingDate=" + bookingDate + ", numberOfPassengers=" + numberOfPassengers +
                ", bookingSeatId=" + bookingSeatId + ", travel=" + travel + ", bookingId=" + bookingId + '}';
    }
    // enter the seats to the flight
       public  int[] bookingSeat(int num){
        int [] arrSeat=new int[num];
        for(int i=0;i<num;i++){
        int addSeatNum=input.nextInt();
         arrSeat[i]=addSeatNum;
        }
        
        return arrSeat;
    }
       // remove the booking seat
       public void returnSeats(ArrayList<Integer>arr){
       for(int i=0;i<arr.size();i++){
       travel.getFlight().cancelSeat(arr.get(i));
       
       }
       
       }
   
      
   public void printTravelList(){
    
    String filePath = "TravelList.txt";

        try {
            // Creating a FileWriter object
            FileWriter fileWriter = new FileWriter(filePath);

            // Creating a PrintWriter object
            PrintWriter printWriter = new PrintWriter(fileWriter);

            // Looping through the array and writing each string to the file
            for (int i=0;i<getBookedTravels().size();i++) {
                String str=getBookedTravels().get(i).toString();
                printWriter.println(str);
            }

            // Closing the PrintWriter
            printWriter.close();

            System.out.println("Strings have been written to the file successfully.");

        } catch (IOException e) {
            System.out.println("An error occurred while writing to the file: " + e.getMessage());
        }
    }
        
} 
