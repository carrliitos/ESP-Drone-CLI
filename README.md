# ESP32 Drone

## Communication Hierarchy

| Terminal          | Mobile/PC           | ESP-Drone               |
|-------------------|---------------------|-------------------------|
| Application Layer | APP                 | Flight Control Firmware |
| Protocol Layer    | CRTP                | CRTP                    |
| Transport Layer   | UDP                 | UDP                     |
| Physical Layer    | Wi-Fi STA (Station) | Wi-Fi AP (Access Point) |

The table in the ESP32 Drone documentation outlines the **communication hierarchy** 
between the user terminal (Mobile/PC) and the ESP-Drone.

### 1. **Application Layer**
 - **Terminal**: Represents the software application running on a mobile or PC 
 that allows the user to interact with the drone.
   - Example: A control app for issuing commands or monitoring status.
 - **ESP-Drone**: Represents the flight control firmware running on the ESP32 
 microcontroller.
   - This firmware handles drone-specific tasks such as stabilization, motor 
   control, and sensor data processing.

### 2. **Protocol Layer**
 - Both the terminal and the drone use the **CRTP (Crazy Real-Time Protocol)**.
   - CRTP is a lightweight protocol designed for low-latency communication in 
   drone systems.
   - It facilitates the exchange of commands and telemetry data between the app 
   and the drone.

### 3. **Transport Layer**
 - **Terminal & Drone**: Communication is transported over **UDP (User Datagram Protocol)**.
   - UDP is chosen for its low overhead and high-speed communication, making it 
   ideal for real-time control where occasional packet loss is acceptable.

### 4. **Physical Layer**
 - **Terminal**: Uses **Wi-Fi in Station (STA) mode**, which connects to the 
 drone's access point.
 - **ESP-Drone**: Operates as a **Wi-Fi Access Point (AP)**, allowing the 
 terminal to establish a direct connection.
   - This setup avoids reliance on external routers and ensures low-latency, 
   point-to-point communication.
---

### **Data Flow**

#### 1. **User Input (Application Layer)**
 - **User Terminal**: 
   - The user interacts with the application on their **Mobile/PC** (e.g., joystick commands, mission planning).
   - The application generates commands or queries in a format compatible with the **Flight Control Firmware**.
 - **ESP-Drone**:
   - The Flight Control Firmware interprets these commands, processes them, and sends back telemetry or status updates.

#### 2. **Protocol Handling (Protocol Layer: CRTP)**
 - Both the terminal and the ESP-Drone use the **Crazy Real-Time Protocol (CRTP)** to package the data.
   - Commands (e.g., "Increase altitude by 2 meters") are encapsulated into CRTP packets by the terminal.
   - Telemetry data (e.g., altitude, battery status) is encapsulated into CRTP packets by the ESP-Drone.
 - CRTP ensures compatibility and synchronization between the app and the firmware.

#### 3. **Data Transmission (Transport Layer: UDP)**
 - The encapsulated CRTP packets are transmitted over **UDP**.
   - Terminal → Drone:
     - The terminal sends control commands to the drone using UDP as the transport protocol.
   - Drone → Terminal:
     - The drone sends telemetry and acknowledgment packets back to the terminal via UDP.

#### 4. **Physical Transmission (Physical Layer: Wi-Fi)**
 - **Wi-Fi AP (Drone)**:
   - The ESP-Drone operates in **Access Point (AP)** mode and provides a Wi-Fi connection.
 - **Wi-Fi STA (Terminal)**:
   - The terminal connects to the drone's Wi-Fi network in **Station (STA)** mode.
   - Data flows over this Wi-Fi link bidirectionally.

### **End-to-End Data Flow (Terminal to Drone and Back)**

1. **User Terminal → ESP-Drone**:
 - Input: **User issues a command** (e.g., increase altitude).
 - Data Flow:
   - **Application Layer**: User command → Encapsulated into CRTP packets.
   - **Protocol Layer**: CRTP packets → Sent over UDP.
   - **Transport Layer**: UDP packets → Transmitted via Wi-Fi STA to Wi-Fi AP.
   - **Physical Layer**: Data received by the ESP-Drone’s Access Point.

2. **ESP-Drone → User Terminal**:
 - Input: **Drone sends telemetry or acknowledgment** (e.g., "Altitude set to 10m").
 - Data Flow:
   - **Physical Layer**: Data sent via Wi-Fi AP to Wi-Fi STA.
   - **Transport Layer**: Data encapsulated in UDP packets.
   - **Protocol Layer**: UDP packets contain CRTP encapsulated telemetry data.
   - **Application Layer**: Terminal app decodes telemetry data and updates the UI.

---

### **Diagram of Data Flow**

```
Terminal (Mobile/PC)                                                        ESP-Drone
|----------------------------|                                     |-------------------------|
|   Application              | <-------- CRTP Packets -------->    | Flight Control Firmware |
|----------------------------|                                     |-------------------------|
        |                                                                       |
        v                                                                       v
|----------------------------|                                     |-----------------------|
|    CRTP (Protocol Layer)   | <--------- Encapsulation ---------> |         CRTP          |
|----------------------------|                                     |-----------------------|
        |                                                                       |
        v                                                                       v
|----------------------------|                                     |-----------------------|
|      UDP (Transport Layer) | <--- Packet Transfer -------------> |         UDP           |
|----------------------------|                                     |-----------------------|
        |                                                                       |
        v                                                                       v
|----------------------------|                                     |---------------------------|
| Wi-Fi STA (Physical Layer) | <--------- Wireless Link ---------> | Wi-Fi AP (Physical Layer) |
|----------------------------|                                     |---------------------------|
```

---

### ESP-Drone Configuration

- **SSID**: ESP-DRONE_6055F9DA14DD
- **MAC Address**: 60:55:F9:DA:14:DD
- **Password**: 12345678
- **IP Address**: 192.168.43.42
- **Port**: 2390

### Per ESP-Drone documenation

UDP Communication
------------------

UDP Port
~~~~~~~~~~

=====================   =================== =======================
App                     Direction           ESP-Drone
=====================   =================== =======================
192.168.43.42::2399     TX/RX               192.168.43.42::2390
=====================   =================== =======================

UDP Packet Structure
~~~~~~~~~~~~~~~~~~~~

```
/* Frame format:
 * +=============+-----+-----+
 * | CRTP                      |   CKSUM   |
 * +=============+-----+-----+
 */
```

- The packet transmitted by the UDP: CRTP + verification information. 
- CRTP: As defined by the CRTP packet structure, it contains Header and Data, as detailed in the CRTP protocol section. 
- CKSUM: the verification information. Its size is 1 byte, and this CKSUM is incremented by CRTP packet byte.
