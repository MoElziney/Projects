/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
package com.mycompany.company;

/**
 *
 * @author MoazE
 */

import com.mycompany.company.Travel;
import java.util.Date;
import java.time.LocalDateTime;
public class BookingEconomyClass extends Booking{
private int priceEconomyclass;

   //constructor
    public BookingEconomyClass() {
        this.travel.getEconomyPrice();
    }

    public BookingEconomyClass( LocalDateTime bookingDate, int numberOfPassengers, int bookingSeatId, Travel travel, int bookingId) {
        super(bookingDate, numberOfPassengers);
        this.priceEconomyclass = this.travel.getEconomyPrice();
    }

    public BookingEconomyClass( String bookingDate, int numberOfPassengers, int bookingSeatId, int bookingId, String departureAirport
            , String destinationAirport, String departureDate, int passengerID, String arrivalDate) {
      super(  bookingDate,  numberOfPassengers,   departureAirport
            ,  destinationAirport,  departureDate,  passengerID,  arrivalDate);
        this.priceEconomyclass = this.travel.getEconomyPrice();
    }
    
    //Setters
      public void setPriceEconomyclass(int priceEconomyclass) {
        this.travel.setEconomyPrice(priceEconomyclass); 
    }
      
    //Getters
   public int getPriceEconomyclass() {
        return this.travel.getEconomyPrice();
    }
   
   @Override
   public int calculateBooking(){
   return getPriceEconomyclass()*getNumberOfPassengers();
    
   }
   //to_string

    @Override
    public String toString() {
           System.out.println("the arrival Date"+this.getArrivalDate());   
        System.out.println("the depature Date"+this.getDepartureDate());   
        System.out.println("thebooking ID "+this.getBookingId()); 
        System.out.println("the price"+this.calculateBooking());

        return "Bookingeconomyclass{" + "priceEconomyclass=" + priceEconomyclass + '}';
    }
   
     
}

