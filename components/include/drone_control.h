/*
 * drone_control.h
 *
 * Created on:         2024-12-02 23:38:27
 *     Author:         carlitos (benzon.salazar@gmail.com)
 *
 * Last Modified by:   carlitos
 * Last Modified time: 2024-12-02 23:48:50
 */

#ifndef MAIN_DRONE_CONTROL_H_
#define MAIN_DRONE_CONTROL_H_

#include <stdint.h>

// CRTP packet structure
typedef struct {
  uint8_t header;      // CRTP header (channel + port)
  uint8_t roll;        // Roll value
  uint8_t pitch;       // Pitch value
  uint8_t yaw;         // Yaw value
  uint8_t thrust;      // Thrust value
} CRTPPacket;

// Handle keyboard input and update control packet
void handle_input(char key);

// Start the drone control system
void start_drone_control(void);

#endif /* MAIN_DRONE_CONTROL_H_ */