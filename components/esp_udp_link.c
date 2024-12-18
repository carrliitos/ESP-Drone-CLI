#include "esp_udp_link.h"
#include "wifi_app.h"
#include "esp_udp_link.h"
#include "esp_log.h"
#include <string.h>
#include <sys/param.h>
#include "lwip/sockets.h"
#include "lwip/netdb.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"

#define TAG "ESPUDPLink"
#define BUFFER_SIZE 1024               // Adjust buffer size as needed
#define HOST_IP_ADDR ESP_DRONE_WIFI_IP // Replace with your server IP
#define HOST_PORT ESP_DRONE_WIFI_PORT  // Replace with your server port

static int udp_socket = -1;
static struct sockaddr_in dest_addr;

// Initialize the UDP socket for communication
void udp_link_init() {
  udp_socket = socket(AF_INET, SOCK_DGRAM, IPPROTO_IP);
  if (udp_socket < 0) {
    ESP_LOGE(TAG, "Failed to create socket: %d", errno);
    return;
  }

  memset(&dest_addr, 0, sizeof(dest_addr));
  dest_addr.sin_family = AF_INET;
  dest_addr.sin_port = htons(HOST_PORT);
  dest_addr.sin_addr.s_addr = inet_addr(HOST_IP_ADDR);

  ESP_LOGI(TAG, "UDP socket initialized. Sending to %s:%d", HOST_IP_ADDR, HOST_PORT);
}

// Send data via UDP
void udp_link_send(const char *message) {
  if (udp_socket < 0) {
    ESP_LOGE(TAG, "Socket not initialized");
    return;
  }

  ssize_t err = sendto(udp_socket, message, strlen(message), 0, (struct sockaddr *)&dest_addr, sizeof(dest_addr));
  if (err < 0) {
    ESP_LOGE(TAG, "Error sending data: %d", errno);
  } else {
    ESP_LOGI(TAG, "Message sent: %s", message);
  }
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

    vTaskDelay(2000 / portTICK_PERIOD_MS); // Wait 2 seconds before next operation
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

// Task to send and receive messages
void udp_client_task(void *pvParameters) {
  udp_link_init();

  const char *payload = "Message from ESP32";
  while (1) {
    udp_link_send(payload); // Send data
    udp_link_receive();     // Receive response

    vTaskDelay(2000 / portTICK_PERIOD_MS); // Wait 2 seconds
  }
}
