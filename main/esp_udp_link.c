/*
 * esp_udp_link.c
 *
 * Created on:         2024-12-02 23:06:28
 *     Author:         carlitos (benzon.salazar@gmail.com)
 *
 * Last Modified by:   carlitos
 * Last Modified time: 2024-12-03 00:13:33
 */

#include "esp_udp_link.h"
#include "esp_log.h"
#include <string.h>
#include <sys/param.h>
#include "lwip/sockets.h"

#define TAG "ESPUDPLink"
#define REMOTE_IP "192.168.43.42"
#define REMOTE_PORT 2390

static int udp_socket = -1;
static struct sockaddr_in remote_addr;

int get_udp_socket() {
  return udp_socket;
}

// Initialize the UDP socket
void udp_link_init() {
  udp_socket = socket(AF_INET, SOCK_DGRAM, IPPROTO_IP);
  if (udp_socket < 0) {
    ESP_LOGE(TAG, "Failed to create socket: %d", errno);
    return;
  }

  remote_addr.sin_family = AF_INET;
  remote_addr.sin_port = htons(REMOTE_PORT);
  inet_aton(REMOTE_IP, &remote_addr.sin_addr);

  ESP_LOGI(TAG, "UDP socket created.");
}

// Send data via UDP
void udp_link_send(const void *data, size_t len) {
  if (udp_socket < 0) {
    ESP_LOGE(TAG, "Socket not initialized");
    return;
  }

  ssize_t sent = sendto(udp_socket, data, len, 0, (struct sockaddr *)&remote_addr, sizeof(remote_addr));
  if (sent < 0) {
    ESP_LOGE(TAG, "Failed to send data: %d", errno);
  } else {
    ESP_LOGI(TAG, "Sent %d bytes via UDP", (int)sent);
  }
}

