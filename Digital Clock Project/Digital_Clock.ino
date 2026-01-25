#include <Wire.h>  // for I2C devices
#include <Adafruit_GFX.h> // for graphical Screens
#include <Adafruit_SSD1306.h> 
#include <RTClib.h> // for date and time

// Define screen width and height for the OLED display and reset pin
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET -1

// Create display object for SSD1306 OLED display
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);
// Create rtc object for DS1307 RTC
RTC_DS1307 rtc;

// Define pin numbers for LED and buttons
const int ledPin = 4;
const int TimerbuttonPin = 2;
const int StopwatchbuttonPin = 3;

 int StopwatchbuttonState = 0;
 int TimerbuttonState = 0;
// Declare a variable to keep track of time
unsigned long Secend;
// Declare a variable to keep track of minutes
int minute = 0;
int i = 0;

// Setup function runs once at the start
void setup() {
  // Initialize I2C communication
  Wire.begin();
  // Begin serial communication at 9600 baud rate
  Serial.begin(9600);
  // Initialize the OLED display
  display.begin(SSD1306_SWITCHCAPVCC, 0x3C);
  // Turn on the OLED display
  display.display();
  // Wait for 2 seconds
  delay(2000);
  // Clear the display
  display.clearDisplay();
  // Begin communication with RTC
  rtc.begin();
  // Set LED pin as output
  pinMode(ledPin,OUTPUT);
  // Set button pins as input
  pinMode(TimerbuttonPin,INPUT);
  pinMode(StopwatchbuttonPin,INPUT);

  // Check if RTC is running, if not, set it to compile time
  if (!rtc.isrunning()) {
    rtc.adjust(DateTime(__DATE__), (__TIME__));
  }
}

// Loop function runs repeatedly
void loop() {
  StopwatchbuttonState = digitalRead(StopwatchbuttonPin);
  TimerbuttonState = digitalRead(TimerbuttonPin);
 // Check if 'StopwatchbuttonState' is 1, indicating button has been pressed
  if(StopwatchbuttonState== HIGH){
    // If time reaches 59 seconds, increment minuteTimer and reset time
    if(Secend == 59){
      minute = minute+1;
      Secend = 0;
    }
    // Turn on the LED
    digitalWrite(ledPin, HIGH);
    // Print the time in minutes and seconds to the serial monitor
    Serial.print("Time: ");
    Serial.print(minute);
    Serial.print(":");
    Serial.print(Secend);
    Serial.println();

    display.clearDisplay();
    display.setCursor(0, 0);
    display.print("Time: ");
    display.print(minute);
    display.print(":");
    Secend = Secend +1;
    display.print(Secend);
    display.println();
    display.display();
    // Wait for 1 second
    delay(1000);
  }
  else if (TimerbuttonState == HIGH) {
    digitalWrite(ledPin, HIGH);

    // Increment the timer by 10 * i seconds
    Secend += 10;

    // // If time is 60 seconds or more
    // if (Secend >= 60) {
    //   // Convert to minutes
    //   minute += Secend / 60;
    //   Secend %= 60; // Keep the remainder in seconds
    // }

    // Print the current time
    Serial.print("Timer: ");
    Serial.print(minute);
    Serial.print(":");
    Serial.println(Secend);
    
    display.clearDisplay();
    display.setCursor(0, 0);
    display.print("Timer: ");
    display.print(minute);
    display.print(":");
    display.println(Secend);
    display.display();

    // Wait for a second before the next loop iteration
   // delay(1000);

    

  // Wait until time and minuteTimer equal zero
  while (minute > 0 || Secend > 0) {
    // Decrement time by 1 every second
    delay(1000);
    if (Secend > 0) {
      Secend -= 1;
    // } else if (minute > 0 && Secend == 0) {
    //   // When time is zero, decrement minuteTimer and reset time to 59
    //   minute -= 1;
    //   Secend = 59;
    // }

    // Print the current time
    Serial.print("Timer: ");
    Serial.print(minute);
    Serial.print(":");
    Serial.println(Secend);

    display.clearDisplay();
    display.setCursor(0, 0);
    display.print("Timer: ");
    display.print(minute);
    display.print(":");
    display.println(Secend);
    display.display();
  }
  }

  else{
    Secend = 0;
    minute = 0;
   // Get the current Date
    DateTime now = rtc.now();
    // Get the current hour and minute from RTC
    int hour = now.hour();
    int minute = now.minute();
    // Call displayTime function to display the time
    digitalWrite(ledPin, LOW);
    displayTime(hour, minute);
  }
}

// Function to display time on OLED
void displayTime(int hour, int minute) {
  // Clear the display
  display.clearDisplay();
  // Set text size for display
  display.setTextSize(1);
  // Set text color for display
  display.setTextColor(WHITE);
  // Set cursor position for display
  display.setCursor(0, 0);   // top left
  // Print "Time: " to the display and serial monitor
  display.print("Time: ");
  Serial.print(F("Time: "));
  // Add leading zero for hours if needed
  if (hour < 10) display.print("0");`
  // Print hour to the display and serial monitor
  display.print((hour+1));
  Serial.print((hour+1));
  // Print colon to the display and serial monitor
  display.print(":");
  Serial.print(":");
  // Add leading zero for minutes if needed
  if (minute < 10) display.print("0");
  if (minute < 10) Serial.print("0");
  // Print minute to the display and serial monitor
  display.println((minute-5));
  Serial.println((minute-5));
  // Update the display
  display.display();
}
