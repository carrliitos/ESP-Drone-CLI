/*
 * autonomous_drone_control.c
 *
 * Created on:         2024-12-03 00:00:27
 *     Author:         carlitos (benzon.salazar@gmail.com)
 *
 * Last Modified by:   carlitos
 * Last Modified time: 2024-12-03 00:19:29
 */

#include "esp_log.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include <sys/socket.h>
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

  struct sockaddr_in source_addr; // Source address for received packets
  socklen_t socklen = sizeof(source_addr);

  while (1) {
    // Send the hover CRTP packet
    udp_link_send(&hover_packet, sizeof(hover_packet));
    ESP_LOGI(TAG, "Sent hover packet.");

    // Wait for acknowledgment or response from the ESP-Drone
    memset(rx_buffer, 0, sizeof(rx_buffer));
    ssize_t len = recvfrom(get_udp_socket(), rx_buffer, sizeof(rx_buffer) - 1, 0, (struct sockaddr *)&source_addr, &socklen);

    if (len < 0) {
      ESP_LOGE(TAG, "recvfrom failed: %d", errno);
    } else if (len > 0) {
      rx_buffer[len] = '\0'; // Null-terminate the received data
      ESP_LOGI(TAG, "Received %d bytes from drone: %s", (int)len, rx_buffer);
    }

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

