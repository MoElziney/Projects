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
public class DataAggregation{
private static ArrayList<Passenger> passengersData=new ArrayList<>();
private static ArrayList<Travel> travelData=new ArrayList<>();
private static ArrayList<Flight> flightsData=new ArrayList<>();
private static ArrayList<Admin> adminsData=new ArrayList<>();
private static ArrayList<Booking> bookingsData=new ArrayList<>();

    public DataAggregation() {
        
    }

    public ArrayList<Booking> getBookingsData() {
        return bookingsData;
    }

    public void setBookingsData(ArrayList<Booking> bookingsData) {
        this.bookingsData = bookingsData;
    }

    public ArrayList<Passenger> getPassengersData() {
        return passengersData;
    }

    public void setPassengersData(ArrayList<Passenger> passengersData) {
        this.passengersData = passengersData;
    }

    public ArrayList<Travel> getTravelData() {
        return travelData;
    }

    public void setTravelData(ArrayList<Travel> travelData) {
        this.travelData = travelData;
    }

    public ArrayList<Flight> getFlightsData() {
        return flightsData;
    }

    public void setFlightsData(ArrayList<Flight> flightsData) {
        this.flightsData = flightsData;
    }

    public ArrayList<Admin> getAdminsData() {
        return adminsData;
    }

    public void setAdminsData(ArrayList<Admin> adminsData) {
        this.adminsData = adminsData;
    }


}

