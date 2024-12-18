#include "drone_control.h"
#include "esp_udp_link.h"
#include "esp_log.h"

#define TAG "DroneControl"

static CRTPPacket control_packet = {0x03, 127, 127, 127, 0}; // Default neutral values

// Handle keyboard input and update the control packet
void handle_input(char key) {
  switch (key) {
    case 'w': control_packet.thrust += 10; break;
    case 's': control_packet.thrust -= 10; break;
    case 'a': control_packet.roll -= 10; break;
    case 'd': control_packet.roll += 10; break;
    case 'z': control_packet.yaw -= 10; break;
    case 'c': control_packet.yaw += 10; break;
    default: return;
  }

  // Ensure thrust values remain within bounds
  if (control_packet.thrust > 255) control_packet.thrust = 255;
  if (control_packet.thrust < 0) control_packet.thrust = 0;

  ESP_LOGI(TAG, "Updated CRTP: Thrust=%d, Roll=%d, Pitch=%d, Yaw=%d",
                control_packet.thrust, control_packet.roll, control_packet.pitch, control_packet.yaw);

  udp_link_send((char *)&control_packet, sizeof(control_packet));
}

// Start drone control (relies on UDP link)
void start_drone_control() {
  udp_link_init();
  ESP_LOGI(TAG, "Drone control started.");
}
