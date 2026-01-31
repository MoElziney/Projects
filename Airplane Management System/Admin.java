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
import java.time.LocalDateTime;
import java.util.Scanner;
import java.util.ArrayList;


public class Admin {
    private String username;
    private String password;
    private String email;
    private String fullName;
    private String phoneNumber;
    private LocalDateTime lastLogin;
    private boolean isActive;
    private LocalDateTime dateCreated;
    private String role;
    private String profilePicture;
    private ArrayList<Travel> dataOfTravels;  
    private ArrayList<Booking> dataOfBookings;
    private ArrayList<Flight> dataOfFlights;



    

    // Constructors
    
    public Admin() {
        dateCreated = LocalDateTime.now();
        username = "";
        password = "";
        email = "";
        fullName = "";
        phoneNumber = "";

        lastLogin = null;
        isActive = false;
        role = "";
        profilePicture = "";
        
       

    }

    public Admin(String username, String password,String email) {
        this.username = username;
        this.password = password;
        this.email = email;
    }

    
    
    // Para Construtor
    public Admin(String usrname, String pwd, String mail, String fname, String phone,
                 String rol, String picture) {
        username = usrname;
        password = pwd;
        email = mail;
        fullName = fname;
        phoneNumber = phone;
        role = rol;
        profilePicture = picture;
        dateCreated = LocalDateTime.now();
       
    }

    // Setters
    public void setUsername(String usrname) {
        username = usrname;
    }

    public void setPassword(String pwd) {
        password = pwd;
    }

    public void setEmail(String mail) {
        email = mail;
    }

    public void setFullName(String fname) {
        fullName = fname;
    }

    public void setPhoneNumber(String phone) {
        phoneNumber = phone;
    }

    public void setLastLogin(LocalDateTime login) {
        lastLogin = login;
    }

    public void setIsActive(boolean active) {
        isActive = active;
    }

    public void setRole(String rol) {
        role = rol;
    }

    public void setProfilePicture(String picture) {
        profilePicture = picture;
    }

    public void setDataOfTravels(ArrayList dataOfTravels) {
        this.dataOfTravels = dataOfTravels;
    }

    public void setDataOfBookings(ArrayList dataOfBookings) {
        this.dataOfBookings = dataOfBookings;
    }

    public void setDataOfFlights(ArrayList dataOfFlights) {
        this.dataOfFlights = dataOfFlights;
    }

   

   

    // Getters
    public String getUsername() {
        return username;
    }

    public String getPassword() {
        return password;
    }

    public String getEmail() {
        return email;
    }

    public String getFullName() {
        return fullName;
    }

    public String getPhoneNumber() {
        return phoneNumber;
    }

    public LocalDateTime getLastLogin() {
        return lastLogin;
    }

    public boolean isActive() {
        return isActive;
    }

    public LocalDateTime getDateCreated() {
        return dateCreated;
    }

    public String getRole() {
        return role;
    }

    public String getProfilePicture() {
        return profilePicture;
    }

    public boolean isIsActive() {
        return isActive;
    }

    public ArrayList getDataOfTravels() {
        return dataOfTravels;
    }

    public ArrayList getDataOfBookings() {
        return dataOfBookings;
    }

    public ArrayList getDataOfFlights() {
        return dataOfFlights;
    }

   
   
    
    // Overriding the toString() function
    
    @Override
    public String toString() {
    return "Admin{" +
            "username='" + username + '\'' +
            ", email='" + email + '\'' +
            ", fullName='" + fullName + '\'' +
            ", phoneNumber='" + phoneNumber + '\'' +
            ", lastLogin=" + lastLogin +
            ", isActive=" + isActive +
            ", dateCreated=" + dateCreated +
            ", role='" + role + '\'' +
            ", profilePicture='" + profilePicture + '\'' +
            '}';
}

   

    // Method to add a new flight
    
    public void addFlight(Flight flight) {
        this.dataOfFlights.add(flight);
    }

    // Method to remove a flight
    
    public Flight removeFlight(int flight_Number) {
        
        for(int i=0;i<dataOfFlights.size();i++){
            Flight temp=dataOfFlights.get(i);
            if(temp.getFlightNumber()==flight_Number){
            return dataOfFlights.remove(i);
            }
        
        }
        return null;
        
    }
    
    // Method to search flights
    
    public boolean searchFlight(int flightNumber){
         ArrayList<Flight>flights=dataOfFlights;
        boolean check = false;
        for(int i = 0; i < flights.size();i++){
            if(flights.get(i).getFlightNumber() == flightNumber){
                check=true ;
           break;}
        }
        return check;
    }
    
    public Flight getFlightByNumber(int flightNumber){
         ArrayList<Flight>flights=dataOfFlights;
        Flight flightSearch=new Flight();
    for(int i = 0; i < flights.size();i++){
            if(flights.get(i).getFlightNumber() == flightNumber){
               flightSearch=flights.get(i);
            break;
            }
        }
    return flightSearch;
    }
    // Method to update flight stored data
    
    public  Admin verifyAccount (String email, String password ,ArrayList<Admin>dataOfAdmins){
      ArrayList <Admin>listOfAdmins=dataOfAdmins;
 Boolean check=false;
      for (int i=0; i<listOfAdmins.size();i++){
//           check= false ;
          if (listOfAdmins.get(i).getEmail().equals(email) && listOfAdmins.get(i).getPassword().equals(password) ){
//           check=true ;
                return listOfAdmins.get(i);
           
          }
    

     }
      return null ;
     }
    
public void updateFlight( int updateFlightNum) {
    
    Flight other ;
        Scanner input= new Scanner(System.in);
        for(int i = 0; i < dataOfFlights.size();i++){
            if(dataOfFlights.get(i).getFlightNumber() == updateFlightNum){
                other=dataOfFlights.get(i);
                
                System.out.println("Which data of the flight do you want to modify:");
                System.out.println("Enter 1 for airline name , 2 for flight number & 3 for capacity:");
                int choose=input.nextInt(i);
                if(choose==1){
                System.out.print ("enter your airline name :");
                String newAirline=input.next();
                other.setAirline(newAirline);
                }else if(choose==2){
                System.out.print ("enter the flight number :");
                int newFlightNumber=input.nextInt();
                other.setFlightNumber(newFlightNumber);
                }else if(choose==3){
                System.out.print ("enter the capacity :");
                int newCapacity=input.nextInt();
                other.setCapacity(newCapacity);
                }
        }
    }
}

// search for the data of booking in a route to generate report about it
public void searchBookingsRoute(String depatureRoute,String arrivalRoute){
  
for(int i=0;i<dataOfBookings.size();i++){
       if(dataOfBookings.get(i).getDepartureAirport().equals(depatureRoute) && dataOfBookings.get(i).getDestinationAirport().equals(arrivalRoute)){
         
           System.out.println(dataOfBookings.get(i));
       }
    }

}

// generate report about the total fare of specific route
public  void reportFareOfRoute(String depatureRoute,String arrivalRoute){
        int totalFare=0;
    for(int i=0;i<dataOfBookings.size();i++){
       if(dataOfBookings.get(i).getDepartureAirport().equals(depatureRoute) && dataOfBookings.get(i).getDestinationAirport().equals(arrivalRoute)){
         
           totalFare+=dataOfBookings.get(i).calculateBooking();
       }
    }
    System.out.println("Total fares of bookings for route " +depatureRoute+ " and "+arrivalRoute+" is "+totalFare);
    }
// generate the all information about the bookings
public void reportFullReport (){
     
int totalFare=0;
int countBookings =0;
for(int i=0;i<dataOfBookings.size();i++){
       {
           totalFare+=dataOfBookings.get(i).calculateBooking();
           countBookings++;
    }
    System.out.println("the total fare of the bookings is : "+totalFare);
    System.out.println("the total number "+countBookings);
}
}  

// view the information about the all flights
public void viewFlight(){
    
    for(int i=0;i<dataOfFlights.size();i++){
        System.out.println(dataOfFlights.get(i));
        
    
    }
    
}

public void AddTravel(Travel t1,ArrayList<Travel>dataOfTravels){
    
    if(CheckTravel(t1,dataOfTravels)){
        System.out.println("not add");
    }
    else{
         dataOfTravels.add(t1);}
    }

public Boolean CheckTravel(Travel t1 ,ArrayList<Travel>dataOfTravels){
        boolean check=false;
            for (int i=0;i<dataOfTravels.size();i++){
             Travel t=(Travel) dataOfTravels.get(i);
            if(t.getFlight().getFlightNumber()==t1.getFlight().getFlightNumber()){
            return true;
             }
              }

            return false ;



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
 
  public void printBookingList(){
    
    String filePath = "BookingsList.txt";

        try {
            // Creating a FileWriter object
            FileWriter fileWriter = new FileWriter(filePath);

            // Creating a PrintWriter object
            PrintWriter printWriter = new PrintWriter(fileWriter);

            // Looping through the array and writing each string to the file
            for (int i=0;i<getDataOfBookings().size();i++) {
                String str=getDataOfBookings().get(i).toString();
                printWriter.println(str);
            }

            // Closing the PrintWriter
            printWriter.close();

            System.out.println("Strings have been written to the file successfully.");

        } catch (IOException e) {
            System.out.println("An error occurred while writing to the file: " + e.getMessage());
        }
    }
  
    public void printFlightList(){
    
    String filePath = "FlightList.txt";

        try {
            // Creating a FileWriter object
            FileWriter fileWriter = new FileWriter(filePath);

            // Creating a PrintWriter object
            PrintWriter printWriter = new PrintWriter(fileWriter);

            // Looping through the array and writing each string to the file
            for (int i=0;i<getDataOfFlights().size();i++) {
                String str=getDataOfFlights().get(i).toString();
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
