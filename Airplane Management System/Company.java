/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 */

package com.mycompany.company;

import java.util.*;

 



/**
 *
 * @author MoazE
 */
public class Company {
   

    // Method to write ArrayList data to a text file
  
public static DataAggregation allOfData=new DataAggregation();

Booking first=new Booking();

    
    public static void main(String[] args) throws Exception{
        Admin ad=new Admin("Moaz","12345","moaz@gmail.com");
        ArrayList<Admin>admins=new ArrayList<>();
        admins.add(ad);
        
        
        Travel tr=new Travel("Cairo","Rome","22-9-2024","22-9-2024","3:00","12:00",new Flight("egyptAir",100,255),10000,8000,5500);
        ArrayList<Travel>travels=new ArrayList<>();
        travels.add(tr);
        Travel tr2=new Travel("Cairo","Istanbul","22-9-2024","22-9-2024","3:00","1:00",new Flight("Turkish AirLines",110,145),9000,7200,5000);
        travels.add(tr2);
        
        ArrayList<Flight> flights=new ArrayList<>();
        Flight f=new Flight("egyptAir",100,255);
        Flight f1=new Flight("Turkish AirLines",110,515);
        Flight f2=new Flight("egyptAir",100,124);
        flights.add(f);    
        flights.add(f1);
        flights.add(f2);

        ArrayList<Passenger>passengers=new ArrayList<>();
        Passenger p=new Passenger("Mariam","635","mariam@gmail.com");
        Passenger p1=new Passenger("Mohamed","623","mohamed@gmail.com");
        passengers.add(p);
        passengers.add(p1);

        allOfData.setAdminsData(admins);
        allOfData.setTravelData(travels);
        allOfData.setFlightsData(flights);
        allOfData.setPassengersData(passengers);
        Login newFrame=new Login();
        newFrame.setVisible(true);
        
        

    }

}

