/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
package com.mycompany.company;

/**
 *
 * @author MoazE
 */
import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.Objects;

public class Travel {
    //Class members
    //departureAirport(string) attribute for airport that the flight will departure from.
    //destinationAirport (String) attributes for airport that the flight will arrival from.
    //departureDate (Date) attribute describe the date that will departure from.
    //arrivalDate (Date) attribute describe the date that will arrival from.
    //arrivalTime(int)  attribute describe the time that flight will arrive in.
    //departureTime(int) attribute attribute describe the time that flight will departure from.
    //flight (object) of class flight to make a aggregation relationship between the two classes.
    //numberOftravel (int) attribute for just counting the number of flight 
    //price(int) attribute for the travel price
    
    
    private String departureAirport;                      //ask about the int arrival
    private String destinationAirport;
    private String departureDate;
    private String arrivalDate;
    private String arrivalTime;
    private String departureTime;
    private Flight flight;
    private int numberOftravel=0;
    private int VIPprice;  
    private int economyPrice;
    private int buisnessPrice;
    private int travelSerialNumber;
    private ArrayList<Travel> dataOfTravels;
  
    //Class methods
    //Default constructor
    
    public Travel() {
        this.departureAirport = "JFK";
        this.destinationAirport = "LAX";
        this.departureDate = null;
        this.arrivalDate = null;
        this.arrivalTime = null;
        this.departureTime = null;
        this.flight = new Flight();
        this.VIPprice = 100;
        this.economyPrice = 50;
        this.buisnessPrice = 95;
        
        
        

    }

 
   
    
    //Paramitarized constructor
   public Travel(String departureAirport, String destinationAirport, String departureDate, 
           String arrivalDate, String arrivalTime, String departureTime, Flight flight, int VIPprice,int economyPrice,int buisnessPrice) {
        this.departureAirport = departureAirport;
        this.destinationAirport = destinationAirport;
        this.departureDate = departureDate;
        this.arrivalDate = arrivalDate;
        this.arrivalTime = arrivalTime;
        this.departureTime = departureTime;
        this.flight = flight;
        this.VIPprice = VIPprice;
        this.economyPrice = economyPrice;
        this.buisnessPrice = buisnessPrice;
        
         
   }
 


 
 
    
    //Setters
     public void setDepartureAirport(String departureAirport) {
        this.departureAirport = departureAirport;
    }

    public void setDestinationAirport(String destinationAirport) {
        this.destinationAirport = destinationAirport;
    }

    public void setDepartureDate(String departureDate) {
        this.departureDate = departureDate;
    }
    

    public void setArrivalDate(String arrivalDate) {
        this.arrivalDate = arrivalDate;
    }

    public void setArrivalTime(String arrivalTime) {
        this.arrivalTime = arrivalTime;
    }

    public void setDepartureTime(String departureTime) {
        this.departureTime = departureTime;
    }

  

    public void setFlight(Flight flight) {
        this.flight = flight;
    }

    public void setNumberOftravel(int numberOftravel) {
        this.numberOftravel = numberOftravel;
    }

    public void setVipPrice(int VIPprice) {
        this.VIPprice = VIPprice;
    }

    public int getVIPprice() {
        return VIPprice;
    }

    public void setVIPprice(int VIPprice) {
        this.VIPprice = VIPprice;
    }

    public int getTravelSerialNumber() {
        return travelSerialNumber;
    }

    public void setTravelSerialNumber(int travelSerialNumber) {
        this.travelSerialNumber = travelSerialNumber;
    }
    public void setEconomyPrice(int economyPrice) {
        this.economyPrice = economyPrice;
    }
    public void setBuisnessPrice(int buisnessPrice) {
        this.buisnessPrice = buisnessPrice;
    }
   
    
   

    
    //Getters
    public String getDepartureAirport() {
        return departureAirport;
    }

    public String getDestinationAirport() {
        return destinationAirport;
    }

    public String getDepartureDate() {
        return departureDate;
    }

    public String getArrivalDate() {
        return arrivalDate;
    }

    public String getArrivalTime() {
        return arrivalTime;
    }

    public String getDepartureTime() {
        return departureTime;
    }

   

    public Flight getFlight() {
        return flight;
    }

    public int getNumberOftravel() {
        return numberOftravel;
    }

    public int getVIPPrice() {
        return VIPprice;
    }
     public int getEconomyPrice() {
        return economyPrice ;
    }
      public int getBuisnessPrice() {
        return buisnessPrice;
    }

    public ArrayList<Travel> getDataOfTravels() {
        return dataOfTravels;
    }
    

   
    //To_String function

    @Override
    public String toString() {
        return "<html>" + "departureAirport:" + departureAirport + "<br> destinationAirport:" + destinationAirport + "<br> departureDate:" + departureDate 
                + "<br> arrivalDate:" + arrivalDate + "<br> arrivalTime:" + arrivalTime + "<br> departureTime:" + departureTime + "<br> flight:" + flight
                + "<br> numberOftravel:" + numberOftravel + "<br> VIPprice:" + VIPprice + "<br> economyPrice:" + economyPrice + "<br> buisnessPrice:" + buisnessPrice + "</html>";
    }

  
  


 
    
    //Class functions
    // The folowing funtion for adding object of the datatype travel to an arraylist called travellist  
    public void addTravel(Travel newTravel ){
      ArrayList<Travel>travelList=dataOfTravels;
       
            travelList.add(newTravel);
        
        numberOftravel++;
       
    }
    
     @Override
    public int hashCode() {
        int hash = 3;
        return hash;
    }
@Override
    public boolean equals(Object obj) {
        if (this == obj) {
            return true;
        }
        if (obj == null) {
            return false;
        }
        if (getClass() != obj.getClass()) {
            return false;
        }
        final Travel other = (Travel) obj;
        if (!this.arrivalTime.equals(other.arrivalTime)) {
            return false;
        }
        if (!this.departureTime.equals(other.departureTime)) {
            return false;
        }
        if (this.numberOftravel != other.numberOftravel) {
            return false;
        }
        if (this.VIPprice != other.VIPprice) {
            return false;
        }
        if (this.economyPrice != other.economyPrice) {
            return false;
        }
        if (this.buisnessPrice != other.buisnessPrice) {
            return false;
        }
        if (!Objects.equals(this.departureAirport, other.departureAirport)) {
            return false;
        }
        if (!Objects.equals(this.destinationAirport, other.destinationAirport)) {
            return false;
        }
        if (!Objects.equals(this.departureDate, other.departureDate)) {
            return false;
        }
        if (!Objects.equals(this.arrivalDate, other.arrivalDate)) {
            return false;
        }
        return Objects.equals(this.flight, other.flight);
    }
    
    //the follwing function foe removing the object of the datatype Travel form the array list that named travellist
    public void removeTravel(int snTravel ){
        ArrayList<Travel>travelList=dataOfTravels;
        for(int i=0;i<travelList.size();i++){
            if(travelList.get(i).getTravelSerialNumber()== snTravel)
            travelList.remove(travelList.get(i));
        }
        numberOftravel--;
       
    }
    //this function for display the travel details for the passenger  
    public void displayAllTravels(ArrayList <Travel> travelList){
       for(int i=0;i<travelList.size();i++){
           Travel currenttravel =(Travel) travelList.get(i);
           System.out.println("Travel Details"+(i+1)+":\n");
           System.out.println("Departure Airport: "+currenttravel.getDepartureAirport());
           System.out.println("Destination Airport: "+currenttravel.getDestinationAirport());
           System.out.println("Arrival Date and Time:: "+currenttravel.getArrivalDate());
           System.out.println("Departure Date and Time:: "+currenttravel.getDepartureDate());
           System.out.println("Flight number : "+flight.getFlightNumber());
           System.out.println("the serial number of the travel :: "+currenttravel.getTravelSerialNumber());
       
       }
   }
  public void displayTravelDetails(){
           System.out.println("Travel Details");
           System.out.println("Departure Airport: "+getDepartureAirport());
           System.out.println("Destination Airport: "+getDestinationAirport());
           System.out.println("Arrival Date and Time:: "+getArrivalDate());
           System.out.println("Departure Date and Time:: "+getDepartureDate());
           System.out.println("Flight number : "+flight.getFlightNumber());
       
       }
   
 public void printTravelList(){
    
    String filePath = "TravelList.txt";

        try {
            // Creating a FileWriter object
            FileWriter fileWriter = new FileWriter(filePath);

            // Creating a PrintWriter object
            PrintWriter printWriter = new PrintWriter(fileWriter);

            // Looping through the array and writing each string to the file
            for (int i=0;i<getDataOfTravels().size();i++) {
                String str=getDataOfTravels().get(i).toString();
                printWriter.println(str);
            }

            // Closing the PrintWriter
            printWriter.close();

            System.out.println("Strings have been written to the file successfully.");

        } catch (IOException e) {
            System.out.println("An error occurred while writing to the file: " + e.getMessage());
        }
    }
 
    
   //this function to calculate the duration of the travel flight 
   
  
    
   //this function allow passenger to know if the flight departure and arrival date 
   //in the same ,if the passenget  wants to know if he will depart and arrive within the say or not
    
    
   //this method computes the duration of a flight based on the departure and arrival times of the travel.
//    public Duration calculateFlightDuration() {
//        return Duration.between(departureTime, arrivalTime);
//    }

    
//this method determines whether the departure and arrival dates of a travel are on the same day.
// It compares the date parts of the departure and arrival LocalDateTime objects and
// returns true if they are the same, and false otherwise. 
    
//     public boolean travelIrensameDay() {
//        if (departureTime.toLocalDate().isEqual(arrivalTime.toLocalDate())) {
//           return true;
//         } 
//        else {
//           return false;
//           }
//      }
    
     
     
     
//This method determines whether a given time falls
// within the time range of a travel. It compares the provided time 
//against the departure and arrival times and returns true 
//if the time is within the interval, and false otherwise. 
//This function is useful for validating input times against scheduled
//travel itineraries in booking systems or ensuring operations occur within specified time frames.  
//   public boolean travelWithinTimeeRange(LocalDateTime time){
//        return arrivalTime.isAfter(departureTime) ;
//   }
   
  
   
   
   
//this method calculates the duration in minutes between the departure and arrival times of a travel.
//This function is useful for obtaining time differences in minutes for scheduling,
// displaying itinerary details, or other time-related computations within travel management systems.
  
//   public long minsBetweenArrivalAndDeparture(){
//        Duration duration = Duration.between(departureTime, arrivalTime);
//        return duration.toMinutes();
//   }

   
   
}
