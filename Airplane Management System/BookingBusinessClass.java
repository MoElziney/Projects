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
public class BookingBusinessClass extends Booking {
    private int priceBusinessclass;
    
    //constructor

    public BookingBusinessClass() {
        this.travel.getBuisnessPrice();
        
    }

    public BookingBusinessClass( LocalDateTime bookingDate, int numberOfPassengers,  Travel travel) {
         super(bookingDate, numberOfPassengers);
        
        this.priceBusinessclass = this.travel.getBuisnessPrice();
    }

    public BookingBusinessClass( String bookingDate, int numberOfPassengers, int bookingSeatId, int bookingId, String departureAirport
            , String destinationAirport, String departureDate, int passengerID, String arrivalDate) {
        super( bookingDate,  numberOfPassengers,   departureAirport
            ,  destinationAirport,  departureDate,  passengerID,  arrivalDate);
        
        this.priceBusinessclass = this.travel.getBuisnessPrice();
    }

  
    
    //Setters

    public void setPriceBusinessclass(int priceBusinessclass) {
        this.travel.setBuisnessPrice(priceBusinessclass);
    }
    
    //Getters

    public int getPriceBusinessclass() {
        return travel.getBuisnessPrice();
    }
    @Override
     public int calculateBooking(){
   return getPriceBusinessclass()*getNumberOfPassengers();
    
   }
    
    @Override
    public String toString() {
        System.out.println("the arrival Date"+this.getArrivalDate());   
        System.out.println("the depature Date"+this.getDepartureDate());   
        System.out.println("thebooking ID "+this.getBookingId()); 
        System.out.println("the price"+this.calculateBooking());



        return "BookingBusinessclass{" + "priceBusinessclass=" + priceBusinessclass + '}';
    }
    
   
}
    
    //Setters

    