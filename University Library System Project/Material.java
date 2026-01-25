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
public class Material {
    private String materialID;
    private int materialYear;
    private String materialTitle;
    private String materialAuthor;
    
    public Material() {
        materialID = "";
        materialYear = 0;
        materialTitle = "";
        materialAuthor = "";
    }

    public Material(String materialID, int materialYear, String materialTitle, String materialAuthor) {
        this.materialID = materialID;
        this.materialYear = materialYear;
        this.materialTitle = materialTitle;
        this.materialAuthor = materialAuthor;
    }

    @Override
    public String toString() {
        return "Material{" + "materialID=" + materialID + ", materialYear=" + materialYear + ", materialTitle=" + materialTitle + ", materialAuthor=" + materialAuthor + '}';
    }
    public void UptadeMaterial(int materialID,String BookName, String author,int PublisherYear,int NofCopies){
 String connectionURL= "jdbc:derby://localhost:1527/ULS";
//ConnectionURL, username and password should be specified in getConnection()
try {
Connection conn = DriverManager.getConnection(connectionURL, "bue", "bue");
String sql = "UPDATE MATERIAL SET BookName='  "+BookName+"' WHERE MaterialID="+materialID+"   ";

Statement st = conn.createStatement();
st.executeUpdate(sql);


sql = "UPDATE MATERIAL SET Author='"+author+"' WHERE MaterialID="+materialID+" ";
st.executeUpdate(sql);


sql = "UPDATE MATERIAL SET PublisherYear='"+PublisherYear+"' WHERE MaterialID="+materialID+" ";
st.executeUpdate(sql);


sql = "UPDATE MATERIAL SET NAME NumberOfCopies='"+NofCopies+"' WHERE MaterialID="+materialID+"";
st.executeUpdate(sql);

st.close();
conn.close();
} catch (SQLException ex) {
System.out.println("Connect failed ! ");
}
 }
}
//    String[] viewAccountList(String  title) {
//    String[] result = null;
//    Connection connection = null;
//    Statement statement = null;
//    ResultSet resultSet = null;
//    
//    try {
//        // Establish database connection
//        connection = DriverManager.getConnection("jdbc:derby://localhost:1527/ULS");
//        statement = connection.createStatement();
//
//        // Execute the query
//        resultSet = statement.executeQuery("SELECT * FROM USER WHERE USERNAME =" + title );
//
//        int i = 0;
//        while (resultSet.next() ) {
//            // Populate the result array with data from the ResultSet
//            String borrowed= "<html>"+resultSet.getInt("USERID")+" ----> "+resultSet.getString("USERNAME")+"<br>"+resultSet.getString("USERROLE") +"</html>";
//            result[i]= borrowed;
//            i++;
//           
//
//        }
//    } catch (SQLException ex) {
//        ex.printStackTrace();
//    } finally {
//        // Close resources in finally block to ensure they are always closed
//        try {
//            if (resultSet != null) resultSet.close();
//            if (statement != null) statement.close();
//            if (connection != null) connection.close();
//        } catch (SQLException ex) {
//            ex.printStackTrace();
//        }
//    }
//
//    return result;
//}
    
    
    
