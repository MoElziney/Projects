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
public class Admin extends User{
    private String adminTitle;

    
    public Admin() {
        adminTitle="";
       
    }
    public Admin(String userName, int userID, String userRole, String userEmail,String adminTitle) {
        // Constructor logic here
        super(userName, userID, userRole, userEmail);
        this.adminTitle=adminTitle;
    }

    public String getAdminTitle() {
        return adminTitle;
    }

    public void setAdminTitle(String adminTitle) {
        this.adminTitle = adminTitle;
    }

    @Override
    public String toString() {
        return "Admin{" + "adminTitle=" + adminTitle + '}';
    }
    
    public void ModifyConstraint(int constraintID,int quantityOFBOOK, int numOFDAYS,int numOFREQUESTS){
 String connectionURL= "jdbc:derby://localhost:1527/buee";
//ConnectionURL, username and password should be specified in getConnection()
try {
Connection conn = DriverManager.getConnection(connectionURL, "bue", "bue");
String sql = "UPDATE MATERIAL SET QUANTITYOFBOOK='  "+quantityOFBOOK+"' WHERE MaterialID="+constraintID+"   ";

Statement st = conn.createStatement();
st.executeUpdate(sql);


sql = "UPDATE MATERIAL SET NUMBEROFDAYS='"+numOFDAYS+"' WHERE MaterialID="+constraintID+" ";
st.executeUpdate(sql);


sql = "UPDATE MATERIAL SET NUMBEROFREQUESTS='"+numOFREQUESTS+"' WHERE MaterialID="+constraintID+" ";
st.executeUpdate(sql);




st.close();
conn.close();
} catch (SQLException ex) {
System.out.println("Connect failed ! ");
}
 }
}
