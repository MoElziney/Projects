/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
package com.mycompany.universitylibrarysystem;

/**
 *
 * @author Computec
 */
public class Magazine extends Material {
    private String magazineName;
    private int numberOfPages;
    private String magazineCategory;

    public Magazine() {
        magazineName = "";
        numberOfPages = 0;
        magazineCategory = "";
    }
    
    

    public Magazine(String magazineName, int numberOfPages, String magazineCategory, String materialID, int materialYear, String materialTitle, String materialAuthor) {
        super(materialID, materialYear, materialTitle, materialAuthor);
        this.magazineName = magazineName;
        this.numberOfPages = numberOfPages;
        this.magazineCategory = magazineCategory;
    }

    @Override
    public String toString() {
        return "Magazine{" + "magazineName=" + magazineName + ", numberOfPages=" + numberOfPages + ", magazineCategory=" + magazineCategory + '}';
    }
    
    
    
}
