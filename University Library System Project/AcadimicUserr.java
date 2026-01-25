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
public class AcadimicUserr extends User {
    private String academicMajor;
    private String academicDepartment;
    private String academicResearchInterests;
    private String academicCurrentStatus;
    
    public AcadimicUserr(){
    academicMajor="";
    academicDepartment="";
    academicResearchInterests="";
    academicCurrentStatus="";
    }   
    

    public AcadimicUserr (String userName, int userID, String userRole,String academicMajor, String academicDepartment, String academicResearchInterests, String academicCurrentStatus) {
    this.academicMajor=academicMajor;
    this.academicDepartment=academicDepartment;
    this.academicResearchInterests=academicResearchInterests;
    this.academicCurrentStatus=academicCurrentStatus;
    }

    public String getAcademicMajor() {
        return academicMajor;
    }

    public void setAcademicMajor(String academicMajor) {
        this.academicMajor = academicMajor;
    }

    public String getAcademicDepartment() {
        return academicDepartment;
    }

    public void setAcademicDepartment(String academicDepartment) {
        this.academicDepartment = academicDepartment;
    }

    public String getAcademicResearchInterests() {
        return academicResearchInterests;
    }

    public void setAcademicResearchInterests(String academicResearchInterests) {
        this.academicResearchInterests = academicResearchInterests;
    }

    public String getAcademicCurrentStatus() {
        return academicCurrentStatus;
    }

    public void setAcademicCurrentStatus(String academicCurrentStatus) {
        this.academicCurrentStatus = academicCurrentStatus;
    }

    @Override
    public String toString() {
        return "AcadimicUserr{" + "academicMajor=" + academicMajor + ", academicDepartment=" + academicDepartment + ", academicResearchInterests=" + academicResearchInterests + ", academicCurrentStatus=" + academicCurrentStatus + '}';
    }
    
    public void addRequest(String bookname, String requestDate, int academicID, int requestID) {
    String connectionURL = "jdbc:derby://localhost:1527/ULS;create=true";
    String username = "";
    String password = "";
    
    try (Connection conn = DriverManager.getConnection(connectionURL);
         PreparedStatement pstmt = conn.prepareStatement("INSERT INTO REQUEST (BOOKNAME, REGUESTDATE, ACADIMIC_ID, REGUESRID) VALUES (?, ?, ?, ?)")) {
        
        pstmt.setString(1, bookname);
        pstmt.setString(2, requestDate);
        pstmt.setInt(3, academicID);
        pstmt.setInt(4, requestID);
        
        int rowsInserted = pstmt.executeUpdate();
        if (rowsInserted > 0) {
            System.out.println("Request added successfully.");
        } else {
            System.out.println("Failed to add request.");
        }
    } catch (SQLException ex) {
        System.out.println("Failed to execute the SQL statement: " + ex.getMessage());
}
}
    public void FeedbackForm(String feedbackdescription, int feedbackid, int academicid) {
    String connectionURL = "jdbc:derby://localhost:1527/ULS;create=true";
    String username = "";
    String password = "";

    try (Connection conn = DriverManager.getConnection(connectionURL);
         PreparedStatement pstmt = conn.prepareStatement("INSERT INTO FEEDBACK (FEEDBACKDISCRIPTION, FEEDBACKID, ACADIMIC_ID) VALUES (?, ?, ?)")) {
        
        pstmt.setString(1, feedbackdescription);
        pstmt.setInt(2, feedbackid);
        pstmt.setInt(3, academicid);
        
        int rowsInserted = pstmt.executeUpdate();
        if (rowsInserted > 0) {
            System.out.println("Feedback added successfully.");
        } else {
            System.out.println("Failed to add feedback.");
        }
    } catch (SQLException ex) {
        System.out.println("Failed to execute the SQL statement: " + ex.getMessage());
}
}
    public String[] manageBorrow(int   id , int row, String newDate) {
    String[] result = null;
    Connection connection = null;
    Statement statement = null;
    ResultSet resultSet = null;

    try {
        // Establish database connection
        connection = DriverManager.getConnection("jdbc:derby://localhost:1527/ULS");
        statement = connection.createStatement();

        // Execute the query
        resultSet = statement.executeQuery("SELECT * FROM BOOKING WHERE BookingID = " + id  );

        int i = 0;
        while (resultSet.next() && i <= row) {
            result = new String[] {resultSet.getInt("BOOKINGID")+"", resultSet.getString("RETURNDATE")};
            i++;
            System.out.print(resultSet.getString("MATERIALID"));
        }

        statement.executeUpdate("UPDATE BOOKING SET RETURNDATE = ' " +  newDate + " ' WHERE BOOKINGID = ' " + result[0] + " ' ");

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
