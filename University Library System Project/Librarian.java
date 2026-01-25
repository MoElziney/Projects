/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
package com.mycompany.universitylibrarysystem;

import java.sql.*;



/**
 *
 * @author home
 */
public class Librarian extends User{
    
    private String librarianTitle;
    private String librarianDepartment;
    private String librarianShift;
    
    
    
     public Librarian() {
        librarianDepartment="";
        librarianShift="";
        librarianTitle="";
    }

    public Librarian(String userName, int userID, String userRole, String userEmail,String librarianTitle, String librarianDepartment, String librarianShift) {
        super(userName, userID, userRole, userEmail);
        this.librarianDepartment=librarianDepartment;
        this.librarianShift=librarianShift;
        this.librarianTitle=librarianTitle;
    
    }

    public String getLibrarianTitle() {
        return librarianTitle;
    }

    public void setLibrarianTitle(String librarianTitle) {
        this.librarianTitle = librarianTitle;
    }

    public String getLibrarianDepartment() {
        return librarianDepartment;
    }

    public void setLibrarianDepartment(String librarianDepartment) {
        this.librarianDepartment = librarianDepartment;
    }

    public String getLibrarianShift() {
        return librarianShift;
    }

    public void setLibrarianShift(String librarianShift) {
        this.librarianShift = librarianShift;
    }

    @Override
    public String toString() {
        return "Librarian{" + "librarianTitle=" + librarianTitle + ", librarianDepartment=" + librarianDepartment + ", librarianShift=" + librarianShift + '}';
    }

    String[] viewKeeptrackDetail(String title) {
    String[] result = new String[100];
    Connection connection = null;
    PreparedStatement statement = null;
    ResultSet resultSet = null;

    try {
        // Establish database connection
        connection = DriverManager.getConnection("jdbc:derby://localhost:1527/ULS");
        
        // Prepare the statement with parameterized query
        String query = "SELECT * FROM BOOKING WHERE BOOKINGID = ?";
        statement = connection.prepareStatement(query, ResultSet.TYPE_SCROLL_INSENSITIVE, ResultSet.CONCUR_READ_ONLY);
        statement.setString(1, title);

        // Execute the query
        resultSet = statement.executeQuery();

        // Initialize the result array with the size of the ResultSet
        
        
        int i = 0;
        while (resultSet.next()) {
            // Populate the result array with data from the ResultSet
            String borrowed = "<html>" + resultSet.getInt("BOOKINGID") + " ----> " + resultSet.getInt("MATERIALID") + "<br>" + resultSet.getInt("ACADEMICID") + "</html>";
            result[i] = borrowed;
            i++;
        }
    } catch (SQLException ex) {
        ex.printStackTrace();
    } finally {
        // Close resources in finally block to ensure they are always closed
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
}
