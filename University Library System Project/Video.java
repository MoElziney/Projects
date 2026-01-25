/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
package com.mycompany.universitylibrarysystem;

/**
 *
 * @author Computec
 */
public class Video extends Material {
    private String videoName;
    private String videoCategory;
    
     public Video() {
        videoName = "";
        videoCategory = "";
    }

    public Video(String videoName, String videoCategory, String materialID, int materialYear, String materialTitle, String materialAuthor) {
        super(materialID, materialYear, materialTitle, materialAuthor);
        this.videoName = videoName;
        this.videoCategory = videoCategory;
    }

    @Override
    public String toString() {
        return "Video{" + "videoName=" + videoName + ", videoCategory=" + videoCategory + '}';
    }
    
    
    
}
