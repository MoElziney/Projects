/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
package com.mycompany.company;

import java.util.ArrayList;

/**
 *
 * @author MoazE
 */
public class Flight {

    private String airline;
    private int capacity;
     private ArrayList<Integer> FlightSeats = new ArrayList<>(capacity);

    public ArrayList<Integer> getFlightSeats() {
        return FlightSeats;
    }

    public void setFlightSeats(ArrayList<Integer> FlightSeats) {
        this.FlightSeats = FlightSeats;
    }
    private int flightNumber;
    private int flightSeatCount;

    public Flight(){
        airline = "No airline name!";
        capacity = 0;
        flightSeatCount = 0;
        flightNumber = 0;
    }

     public Flight(String air, int capacity, int flightNimber) {
        this.airline = air;
        this.capacity = capacity;
        this.flightNumber = flightNimber;
        flightSeatCount = 0;
        
        generateSeats();
        
    }

    @Override
    public String toString() {
        return "<html>" + "airline:" + airline + "<br> capacity:" + capacity  + "<br> flightNumber:" + flightNumber  + "</html>" ;
    }

    //increase number of seat which is already booked

    public boolean checkAvailableSeat(int key){
        boolean check=false;
    for(int i=0;i<FlightSeats.size();i++){
    if(FlightSeats.get(i)==key){
    check=true;
        
        break;
    
    }
    
    }
    return check;
    }
    // add dynamicly the seats to the array of seats depend on the capacity
    private  void  generateSeats(){
        for(int i = 0; i<= capacity; i++){
            FlightSeats.add(i+1);
        }
    }
    
    //remove the seat which is booked from the array of available seats
    public  void  bookSeat (int key){
     
      for (int i=0; i<FlightSeats.size();i++){
          if (FlightSeats.get(i)==key ){
           FlightSeats.remove(i);
           break;
          }
    flightSeatCount++;

     }
      
      
     }

    // add the cancel booked seat to the array of available seats on the flight
    public  void  cancelSeat (int key){
     
           FlightSeats.add(key);
           flightSeatCount--;
     }
    
    // check if the flight is full
    public boolean isFull(){
        if(flightSeatCount < capacity)
            return true;
        else
            return false;
    }

    public ArrayList<Integer> getFlightSeat() {
        return FlightSeats;
    }

    public void setFlightSeat(int flightSeat) {
        this.flightSeatCount = flightSeat;
        generateSeats();
    }

    
    public String getAirline() {
        return airline;
    }

    public void setAirline(String airline) {
        this.airline = airline;
    }

    public int getCapacity() {
        return capacity;
    }

    public void setCapacity(int capacity) {
        this.capacity = capacity;
    }

    public int getFlightNumber() {
        return flightNumber;
    }

    public void setFlightNumber(int flightNumber) {
        this.flightNumber = flightNumber;
    }

    
    }

