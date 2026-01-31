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
import java.util.ArrayList;
public class BookingVIPClass extends Booking{
    //attributes
    
    private int VIPprice;
    private String extraRequests;
    
    //Constructor
    public BookingVIPClass() {
        this.travel.getVIPPrice();
    }

    public BookingVIPClass( LocalDateTime bookingDate, int numberOfPassengers,
             Travel travel, String extra) {
        super(bookingDate, numberOfPassengers);
        this.extraRequests=extra;
        this.VIPprice = this.travel.getVIPPrice();
    }

    public BookingVIPClass( String bookingDate, int numberOfPassengers,  String departureAirport
            , String destinationAirport, String departureDate, int passengerID, String arrivalDate,String extra) {
        super(  bookingDate,  numberOfPassengers,   departureAirport
            ,  destinationAirport,  departureDate,  passengerID,  arrivalDate);
        this.extraRequests=extra;
        this.VIPprice = this.travel.getVIPPrice();
    }
    
    //Setters

    public void setVIPprice(int VIPprice) {
        this.travel.setVipPrice(VIPprice);
    }
    
    //Getters
    public int getVIPprice() {
        return travel.getVIPPrice();
    }
    
    //to_string
    @Override
    public int calculateBooking(){
     return getVIPprice()*getNumberOfPassengers();
    
   }
    @Override
    public String toString() {
           System.out.println("the arrival Date"+this.getArrivalDate());   
        System.out.println("the depature Date"+this.getDepartureDate());   
        System.out.println("thebooking ID "+this.getBookingId()); 
        System.out.println("the price"+this.calculateBooking());

        
        return "BookingVIPclass{" + "VIPprice=" + VIPprice + '}';
    }
    
    
}
