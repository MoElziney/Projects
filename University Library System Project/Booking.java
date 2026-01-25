/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
package com.mycompany.universitylibrarysystem;

import java.sql.*;

/**
 *
 * @author Computec
 */
public class Booking {
    private String returnDate;
    private String bookingID;
    private String borrower;
    private String dateBorrowed;
    private String deadlineDate;
    
    
    public Booking() {
        returnDate = "";
        bookingID = "";
        borrower = "";
        dateBorrowed = "";
        deadlineDate = "";
    }
    

    public Booking(String dateOfPublication, String bookingID, String borrower, String dateBorrowed, String deadlineDate) {
        this.returnDate = dateOfPublication;
        this.bookingID = bookingID;
        this.borrower = borrower;
        this.dateBorrowed = dateBorrowed;
        this.deadlineDate = deadlineDate;
    }

    @Override
    public String toString() {
        return "Booking{" + "dateOfPublication=" + returnDate + ", bookingID=" + bookingID + ", borrower=" + borrower + ", dateBorrowed=" + dateBorrowed + ", deadlineDate=" + deadlineDate + '}';
    }
    
    public String[] viewBookingList(  int academicID) {
    String[] result = new String[100]; // Initialize the result array
    Connection connection = null;
    Statement statement = null;
    ResultSet resultSet = null;

    try {
        // Establish database connection
        connection = DriverManager.getConnection("jdbc:derby://localhost:1527/ULS");
        statement = connection.createStatement();

        // Execute the query
        resultSet = statement.executeQuery("SELECT * FROM BOOKING WHERE  ACADEMICID = " + academicID);

        int i = 0;
        // Populate the result array with data from the ResultSet
        while (resultSet.next() && i < result.length) {
            String borrowed = "<html>" + resultSet.getInt("BOOKINGID") + " ----> " + resultSet.getString("MATERIALID") + "<br>" + resultSet.getString("RETURNDATE") + "</html>";
            result[i] = borrowed;
            i++;
        }
    } catch (SQLException ex) {
        ex.printStackTrace();
    } finally {
        // Close resources in the finally block to ensure they are always closed
        
        try {
            if (resultSet != null) resultSet.close();
            if (statement != null) statement.close();
            if (connection != null) connection.close();
        } catch (SQLException ex) {
            ex.printStackTrace();
        }
    }

    return result;
    
}
    String[] viewBookingDetail( int academicID, int row) {
    String[] result = null;
    Connection connection = null;
    Statement statement = null;
    ResultSet resultSet = null;

    try {
        // Establish database connection
        connection = DriverManager.getConnection("jdbc:derby://localhost:1527/ULS");
        statement = connection.createStatement();

        // Execute the query
        resultSet = statement.executeQuery("SELECT * FROM BOOKING WHERE  ACADEMICID = " + academicID);

        int i = 0;
        while (resultSet.next() && i <= row) {
            result = new String[]{
                String.valueOf(resultSet.getInt("BookingID")),
                String.valueOf(resultSet.getInt("MATERIALID")),
                resultSet.getString("ACADEMICID"),
                
            };
            i++;
            
        }

        // Update ReturnDate
        
    } catch (SQLException ex) {
        ex.printStackTrace();
    } finally {
        try {
            // Close connections
            if (resultSet != null) resultSet.close();
            if (statement != null) statement.close();
            if (connection != null) connection.close();
        } catch (SQLException ex) {
            ex.printStackTrace();
        }
    }
return result;
}
  public void bookingDetail(int bookingID, int academicID, int materialID, String returnDate, String borrowDate,String status) {
    Connection connection = null;
    Statement statement = null;

    try {
        // Establish database connection
        connection = DriverManager.getConnection("jdbc:derby://localhost:1527/ULS");
        statement = connection.createStatement();

        // Execute the INSERT query
         statement.executeUpdate("INSERT INTO BOOKING (BOOKINGID, RETURNDATE, BORROWDATE, MATERIALID, ACADEMICID,STATUS) VALUES (" + bookingID + ", '" + returnDate + "', '" + borrowDate + "', " + materialID + ", " + academicID + ","+status+")");
        
       

    } catch (SQLException ex) {
        ex.printStackTrace();
    } finally {
        try {
            // Close connections
            if (statement != null) statement.close();
            if (connection != null) connection.close();
        } catch (SQLException ex) {
            ex.printStackTrace();
        }
    }
}
  public void returnBook(int BookingID) {
    String connectionURL = "jdbc:derby://localhost:1527/ULS;create=true";
    String username = ""; // Add your username if applicable
    String password = ""; // Add your password if applicable
    
    // ConnectionURL, username, and password should be specified in getConnection()
    try {
        Connection conn = DriverManager.getConnection(connectionURL);
        
        // Delete booking
        String deleteSql = "DELETE FROM BOOKING WHERE BOOKINGID=?";
        PreparedStatement deleteStatement = conn.prepareStatement(deleteSql);
        deleteStatement.setInt(1, BookingID);
        deleteStatement.executeUpdate();
        deleteStatement.close();

        // Insert feedback
        

        conn.close();
    } catch (SQLException ex) {
        System.out.println("Connect failed: " + ex.getMessage());
    }
}
}
