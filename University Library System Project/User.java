/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
package com.mycompany.universitylibrarysystem;

import java.sql.*;
import java.util.logging.Level;
import java.util.logging.Logger;




/**
 *
 * @author home
 */
public class User {
    private String userName;
    private int userID;
    private String userRole;
    private String userEmail;
    
    
    
    public User(){
        userName = "";
        userID = 0;
        userRole = "";
        userEmail ="";
    }

    public User(String userName, int userID, String userRole, String userEmail) {
        this.userName = userName;
        this.userID = userID;
        this.userRole = userRole;
        this.userEmail = userEmail;
    }

    public String getUserName() {
        return userName;
    }

    public void setUserName(String userName) {
        this.userName = userName;
    }

    public int getUserID() {
        return userID;
    }

    public void setUserID(int userID) {
        this.userID = userID;
    }

    public String getUserRole() {
        return userRole;
    }

    public void setUserRole(String userRole) {
        this.userRole = userRole;
    }

    public String getUserEmail() {
        return userEmail;
    }

    public void setUserEmail(String userEmail) {
        this.userEmail = userEmail;
    }

    @Override
    public String toString() {
        return "User{" + "userName=" + userName + ", userID=" + userID + ", userRole=" + userRole + ", userEmail=" + userEmail + '}';
    }

   
    
public  boolean checkAccount(String username,int password){
        boolean c = false;
        String connectionURL= "jdbc:derby://localhost:1527/ULS";
        try {
            Connection connection = DriverManager.getConnection(connectionURL);
Statement st = connection.createStatement();
ResultSet rs=null;
String sql = "SELECT * FROM ACCOUNT";
rs=st.executeQuery(sql);

while(rs.next()){
 if(rs.getString("ACCOUNTUSERNAME").equals(username) && rs.getString("ACCOUNTPASSWORD").equals(password)){
     
     this.setUserID(rs.getInt("USERID"));
    c = true;
    break;
 }
 
}

 } catch (SQLException ex) {
            Logger.getLogger(SignUp.class.getName()).log(Level.SEVERE, null, ex);
        }
        
  return c;     
}

public boolean check(String email){
        boolean c = true;
        String connectionURL= "jdbc:derby://localhost:1527/ULS";
        try {
            Connection connection = DriverManager.getConnection(connectionURL);
Statement st = connection.createStatement();
ResultSet rs=null;
String sql = "SELECT * FROM USER12";
rs=st.executeQuery(sql);

while(rs.next()){
 if(rs.getString("USEREMAIL").equals(email)){
    c = false;
    break;
 }
 
}

 } catch (SQLException ex) {
            Logger.getLogger(SignUp.class.getName()).log(Level.SEVERE, null, ex);
        }
  
        return c;
}

   public boolean VerifyNewAccount(int userID,String email, String name, int password, String academicmajor,
                                String academicDepartment, String academicResearchInterests, String academicCurrentStatus) {
    String connectionURL = "jdbc:derby://localhost:1527/ULS";
    try (Connection connection = DriverManager.getConnection(connectionURL)) {
        // Check if the email already exists
        if (check(email)) {
            // Insert user details into USER12 table
            String insertUserQuery = "INSERT INTO USER12(USERNAME, USEREMAIL, USERROLE, USERID) VALUES (?, ?, 'Academic', ?"
                    + ")";
            try (PreparedStatement userStatement = connection.prepareStatement(insertUserQuery)) {
                userStatement.setString(1, name);
                userStatement.setString(2, email);
                userStatement.setInt(4, userID);
                userStatement.executeUpdate();
            }

            // Insert account password into ACCOUNT table
            String insertAccountQuery = "INSERT INTO ACCOUNT(USERID,ACCOUNTPASSWORD, ACCOUNTUSERNAME) VALUES (?,? ,?)";
            try (PreparedStatement accountStatement = connection.prepareStatement(insertAccountQuery)) {
                accountStatement.setInt(1, userID);
                accountStatement.setInt(2, password);
                accountStatement.setString(3, name);
                accountStatement.executeUpdate();
            }

            // Insert academic details into ACADEMIC table
            String insertAcademicQuery = "INSERT INTO ACADEMIC(ACADEMICID,DEPARTMENT, RESEARCHINTERESTS, MAJOR, CURRENTSTATUS) VALUES (?,?, ?, ?, ?)";
            try (PreparedStatement academicStatement = connection.prepareStatement(insertAcademicQuery)) {
                academicStatement.setInt(1, userID);
                academicStatement.setString(2, academicDepartment);
                academicStatement.setString(3, academicResearchInterests);
                academicStatement.setString(4, academicmajor);
                academicStatement.setString(5, academicCurrentStatus);
                academicStatement.executeUpdate();
            }

            return true; // Account creation successful
        } else {
            System.out.println("Email already exists.");
            return false; // Account creation failed
        }
    } catch (SQLException ex) {
        ex.printStackTrace();
        return false; // Account creation failed
}
}
    
}
