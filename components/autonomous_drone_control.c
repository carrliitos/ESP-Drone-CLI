#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include <string.h>
#include <errno.h>

#include "autonomous_drone_control.h"
#include "esp_udp_link.h"

#define TAG "AutonomousControl"

// Default CRTP packet for hovering
static CRTPPacket hover_packet = {0x03, 127, 127, 127, 150}; // Neutral roll/pitch/yaw, stable thrust

// Buffer to hold received data
static char rx_buffer[128];

// Task to send hover packets periodically, waiting for acknowledgment
static void hover_task(void *pvParameters) {
  ESP_LOGI(TAG, "Starting hover task...");

  while (1) {
    // Send the hover CRTP packet
    udp_link_send((char *)&hover_packet, sizeof(hover_packet));
    ESP_LOGI(TAG, "Sent hover packet.");

    // Delay before the next iteration
    vTaskDelay(pdMS_TO_TICKS(100));
  }
}

// Function to start autonomous control
void start_autonomous_control() {
  ESP_LOGI(TAG, "Starting autonomous control...");

  // Initialize the UDP socket
  udp_link_init();

  // Start the hover task
  xTaskCreate(hover_task, "hover_task", 4096, NULL, 5, NULL);
}
