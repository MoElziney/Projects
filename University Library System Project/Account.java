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
public class Account {
     private String userName;
     private String accountPassword; // String data type.

    public Account() {
        userName = "";
        accountPassword = "";
    }
     
     

    public Account(String userName, String accountPassword) {
        this.userName = userName;
        this.accountPassword = accountPassword;
    }

    @Override
    public String toString() {
        return "Account{" + "userName=" + userName + ", accountPassword=" + accountPassword + '}';
    }
     
     
}
