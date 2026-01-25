/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
package com.mycompany.universitylibrarysystem;

import java.sql.*;



/**
 *
 * @author MoazE
 */
public class Book extends Material{
    int bookNumberOfPages;
    String bookCategory;
    int bookNumberOfCopies;
    String bookImage;

    public void setBookNumberOfPages(int bookNumberOfPages) {
        this.bookNumberOfPages = bookNumberOfPages;
    }

    public void setBookCategory(String bookCategory) {
        this.bookCategory = bookCategory;
    }

    public void setBookNumberOfCopies(int bookNumberOfCopies) {
        this.bookNumberOfCopies = bookNumberOfCopies;
    }

    public int getBookNumberOfPages() {
        return bookNumberOfPages;
    }

    public String getBookCategory() {
        return bookCategory;
    }

    public int getBookNumberOfCopies() {
        return bookNumberOfCopies;
    }
    public  String[] listBookDetail(String  title) {
    String[] result = null;
    Connection connection = null;
    Statement statement = null;
    ResultSet resultSet = null;
    
    try {
        // Establish database connection
        connection = DriverManager.getConnection("jdbc:derby://localhost:1527/ULS");
        statement = connection.createStatement();

        // Execute the query
        resultSet = statement.executeQuery("SELECT MATERIALID, MATERIALAUTHOR, MATERIALYEAR, BOOKNAME, NUMBEROFPAGES, BOOKCATEGORY, NUMBEROFCOPIES " +
                "FROM MATERIAL " +
                "JOIN BOOK ON MATERIALID = BOOKID " +
                "WHERE BOOKNAME LIKE '" + title + "%'");
        
        int i=0;
        while(resultSet.next()){
        String printTemp="<html><div style= \"border: 1px solid black; padding: 2px 100px 2px 2px;\"><img src= \"\" ><div>"
                + resultSet.getString("BOOKNAME")+"<br> "+resultSet.getString("MATERIALAUTHOR")+"</div></div></html>";
        result[i]=printTemp;
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
    public  String[] viewMagazineDetail(String  title, int row) {
    String[] result = null;
    Connection connection = null;
    Statement statement = null;
    ResultSet resultSet = null;
    
    try {
        // Establish database connection
        connection = DriverManager.getConnection("jdbc:derby://localhost:1527/ULS");
        statement = connection.createStatement();

        // Execute the query
        resultSet = statement.executeQuery("SELECT MATERIALID, MATERIALAUTHOR, MATERIALYEAR, MAGAZINENAME, NUMBEROFPAGES, MAGAZINECATEGORY, NUMBER_OF_COPIES " +
                "FROM MATERIAL " +
                "JOIN MAGAZINE ON MATERIALID = MAGAZINEID " +
                "WHERE MAGAZINENAME LIKE '" + title + "%'");
        
        int i = 0;
        while (resultSet.next() && i <= row) {
            // Populate the result array with data from the ResultSet
            result = new String[] {
                resultSet.getString("MATERIALID"),
                resultSet.getString("MATERIALAUTHOR"),
                resultSet.getString("MATERIALYEAR"),
                resultSet.getString("MAGAZINENAME"),
                resultSet.getString("NUMBEROFPAGES"),
                resultSet.getString("MAGAZINECATEGORY"),
                resultSet.getString("NUMBER_OF_COPIES")
            };
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
    public  String[] viewBookMagazineDetail(String  title, int row) {
    String[] result = null;
    Connection connection = null;
    Statement statement = null;
    ResultSet resultSet = null;
    
    try {
        // Establish database connection
        connection = DriverManager.getConnection("jdbc:derby://localhost:1527/ULS");
        statement = connection.createStatement();

        // Execute the query
        resultSet = statement.executeQuery("SELECT MATERIALID, MATERIALAUTHOR, MATERIALYEAR, BOOKNAME, NUMBEROFPAGES, BOOKCATEGORY, NUMBEROFCOPIES " +
                "FROM MATERIAL " +
                "JOIN BOOK ON MATERIALID = BOOKID " +
                "WHERE BOOKNAME LIKE '" + title + "%'");
        
        int i = 0;
        while (resultSet.next() && i <= row) {
            // Populate the result array with data from the ResultSet
            result = new String[] {
                resultSet.getString("MATERIALID"),
                resultSet.getString("MATERIALAUTHOR"),
                resultSet.getString("MATERIALYEAR"),
                resultSet.getString("BOOKNAME"),
                resultSet.getString("NUMBEROFPAGES"),
                resultSet.getString("BOOKCATEGORY"),
                resultSet.getString("NUMBEROFCOPIES")
            };
            i++;
            System.out.print(resultSet.getString("MATERIALID"));
        
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
public  String[] viewBookDetail(String  title) {
    String[] result = null;
    Connection connection = null;
    Statement statement = null;
    ResultSet resultSet = null;
    
    try {
        // Establish database connection
        connection = DriverManager.getConnection("jdbc:derby://localhost:1527/ULS");
        statement = connection.createStatement();

        // Execute the query
        resultSet = statement.executeQuery("SELECT MATERIALID, MATERIALAUTHOR, MATERIALYEAR, BOOKNAME, NUMBEROFPAGES, BOOKCATEGORY, NUMBEROFCOPIES " +
                "FROM MATERIAL " +
                "JOIN BOOK ON MATERIALID = BOOKID " +
                "WHERE BOOKNAME LIKE '" + title + "%'");
        
        int i=0;
        while(resultSet.next()){
        String printTemp="<html><div style= \"border: 1px solid black; padding: 2px 100px 2px 2px;\"><img src= \"\" ><div>"
                + resultSet.getString("BOOKNAME")+"<br> "+resultSet.getString("MATERIALAUTHOR")+"</div></div></html>";
        result[i]=printTemp;
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