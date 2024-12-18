/*
 * esp_udp_link.c
 *
 * Created on:         2024-12-02 23:06:28
 *     Author:         carlitos (benzon.salazar@gmail.com)
 *
 * Last Modified by:   carrliitos
 * Last Modified time: 2024-12-07 20:18:03
 */

#include "esp_udp_link.h"
#include "wifi_app.h"
#include "esp_log.h"
#include <string.h>
#include <sys/param.h>
#include "lwip/sockets.h"

#define TAG "ESPUDPLink"
#define BUFFER_SIZE 1024 // Adjust buffer size as needed

static int udp_socket = -1;

// Initialize the UDP socket for receiving data
void udp_link_init() {
  struct sockaddr_in local_addr;

  // Create UDP socket
  udp_socket = socket(AF_INET, SOCK_DGRAM, IPPROTO_IP);
  if (udp_socket < 0) {
    ESP_LOGE(TAG, "Failed to create socket: %d", errno);
    return;
  }

  // Bind the socket to the local port
  memset(&local_addr, 0, sizeof(local_addr));
  local_addr.sin_family = AF_INET;
  local_addr.sin_port = htons(ESP_DRONE_WIFI_PORT);
  local_addr.sin_addr.s_addr = INADDR_ANY;

  if (bind(udp_socket, (struct sockaddr *)&local_addr, sizeof(local_addr)) < 0) {
    ESP_LOGE(TAG, "Failed to bind socket: %d", errno);
    close(udp_socket);
    udp_socket = -1;
    return;
  }

  ESP_LOGI(TAG, "UDP socket initialized and bound to port %d", ESP_DRONE_WIFI_PORT);
}

// Receive data via UDP
void udp_link_receive() {
  if (udp_socket < 0) {
    ESP_LOGE(TAG, "Socket not initialized");
    return;
  }

  char buffer[BUFFER_SIZE];
  struct sockaddr_in source_addr;
  socklen_t addr_len = sizeof(source_addr);

  while (1) {
    // Receive data
    ssize_t received = recvfrom(udp_socket, buffer, BUFFER_SIZE - 1, 0, (struct sockaddr *)&source_addr, &addr_len);
    if (received < 0) {
      ESP_LOGE(TAG, "Failed to receive data: %d", errno);
      break;
    } else {
      buffer[received] = '\0'; // Null-terminate the received data
      ESP_LOGI(TAG, "Received %d bytes from %s:%d: %s", 
               (int)received, 
               inet_ntoa(source_addr.sin_addr), 
               ntohs(source_addr.sin_port), 
               buffer);
    }
  }
}

// Close the UDP socket
void udp_link_close() {
  if (udp_socket >= 0) {
    close(udp_socket);
    udp_socket = -1;
    ESP_LOGI(TAG, "UDP socket closed.");
  }
}
