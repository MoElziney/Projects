/*
 * Click nbfs://nbhost/SystemFileSystem/Templates/Licenses/license-default.txt to change this license
 * Click nbfs://nbhost/SystemFileSystem/Templates/Classes/Class.java to edit this template
 */
package Classes;

import java.io.*;

/**
 *
 * @author Mohamed Khaled
 */
public class TShirt implements Serializable {
    private String size;
    private String color;
    private String fabric;

    public TShirt(String size, String color, String fabric) {
        this.size = size;
        this.color = color;
        this.fabric = fabric;
    }

    
    
    public String getSize() {
        return size;
    }

    public void setSize(String size) {
        this.size = size;
    }

    public String getColor() {
        return color;
    }

    public void setColor(String color) {
        this.color = color;
    }

    public String getFabric() {
        return fabric;
    }

    public void setFabric(String fabric) {
        this.fabric = fabric;
    }

    @Override
    public String toString() {
        return "TShirt{" + "size=" + size + ", color=" + color + ", fabric=" + fabric + '}';
    }
    
    
}
