/**
 * wifi_app.c
 */
#include <string.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/event_groups.h"
#include "esp_system.h"
#include "esp_wifi.h"
#include "esp_event.h"
#include "esp_log.h"
#include "nvs_flash.h"

#include "wifi_app.h"

static EventGroupHandle_t s_wifi_event_group;  // FreeRTOS event group to signal when we are connected
static const char *TAG = "wifi station";
static int s_retry_num = 0;

static void event_handler(void *arg, esp_event_base_t event_base, int32_t event_id, void *event_data) {
  if (event_base == WIFI_EVENT && event_id == WIFI_EVENT_STA_START) {
    esp_wifi_connect();
  } else if (event_base == WIFI_EVENT && event_id == WIFI_EVENT_STA_DISCONNECTED) {
  if (s_retry_num < ESP_DRONE_MAXIMUM_RETRY) {
    esp_wifi_connect();
    s_retry_num++;
    ESP_LOGI(TAG, "retry to connect to the AP");
  } else {
    xEventGroupSetBits(s_wifi_event_group, WIFI_FAIL_BIT);
  }
  ESP_LOGI(TAG, "connect to the AP failed");
  } else if (event_base == IP_EVENT && event_id == IP_EVENT_STA_GOT_IP) {
    ip_event_got_ip_t *event = (ip_event_got_ip_t *)event_data;
    ESP_LOGI(TAG, "got ip:" IPSTR, IP2STR(&event->ip_info.ip));
    s_retry_num = 0;
    xEventGroupSetBits(s_wifi_event_group, WIFI_CONNECTED_BIT);
  }
}

void wifi_app_start(void) {
  s_wifi_event_group = xEventGroupCreate();

  ESP_ERROR_CHECK(esp_netif_init());
  ESP_ERROR_CHECK(esp_event_loop_create_default());
  esp_netif_create_default_wifi_sta();

  wifi_init_config_t cfg = WIFI_INIT_CONFIG_DEFAULT();
  ESP_ERROR_CHECK(esp_wifi_init(&cfg));

  esp_event_handler_instance_t instance_any_id;
  esp_event_handler_instance_t instance_got_ip;
  ESP_ERROR_CHECK(esp_event_handler_instance_register(WIFI_EVENT,
                                                      ESP_EVENT_ANY_ID,
                                                      &event_handler,
                                                      NULL,
                                                      &instance_any_id));
  ESP_ERROR_CHECK(esp_event_handler_instance_register(IP_EVENT,
                                                      IP_EVENT_STA_GOT_IP,
                                                      &event_handler,
                                                      NULL,
                                                      &instance_got_ip));

  wifi_config_t wifi_config = {
    .sta = {
      .ssid     = ESP_DRONE_WIFI_SSID,
      .password = ESP_DRONE_WIFI_PASS,
    },
  };

  strncpy((char *)wifi_config.sta.ssid, ESP_DRONE_WIFI_SSID, sizeof(wifi_config.sta.ssid));
  strncpy((char *)wifi_config.sta.password, ESP_DRONE_WIFI_PASS, sizeof(wifi_config.sta.password));

  ESP_ERROR_CHECK(esp_wifi_set_mode(WIFI_MODE_STA));
  ESP_ERROR_CHECK(esp_wifi_set_config(WIFI_IF_STA, &wifi_config));
  ESP_ERROR_CHECK(esp_wifi_start());

  ESP_LOGI(TAG, "wifi_app_start finished.");

  EventBits_t bits = xEventGroupWaitBits(s_wifi_event_group,
                                         WIFI_CONNECTED_BIT | WIFI_FAIL_BIT,
                                         pdFALSE,
                                         pdFALSE,
                                         portMAX_DELAY);

  if (bits & WIFI_CONNECTED_BIT) {
    ESP_LOGI(TAG, "***Connected to AP SSID:%s password:%s", ESP_DRONE_WIFI_SSID, ESP_DRONE_WIFI_PASS);
  } else if (bits & WIFI_FAIL_BIT) {
    ESP_LOGI(TAG, "Failed to connect to SSID:%s, password:%s", ESP_DRONE_WIFI_SSID, ESP_DRONE_WIFI_PASS);
  } else {
    ESP_LOGE(TAG, "UNEXPECTED EVENT");
  }
}

