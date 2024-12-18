#ifndef MAIN_WIFI_APP_H
#define MAIN_WIFI_APP_H

#include <esp_err.h>

// Wi-Fi constants
#define ESP_DRONE_WIFI_SSID      "ESP-DRONE_6055F9DA14DD"
#define ESP_DRONE_WIFI_PASS      "12345678"
#define ESP_DRONE_WIFI_IP        "192.168.43.42"
#define ESP_DRONE_WIFI_PORT      2399
#define ESP_DRONE_MAXIMUM_RETRY  5
#define WIFI_CONNECTED_BIT       BIT0
#define WIFI_FAIL_BIT            BIT1

/**
 * Starts the WiFi RTOS task
 */
void wifi_app_start(void);

#endif /* MAIN_WIFI_APP_H */