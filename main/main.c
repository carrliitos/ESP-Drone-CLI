#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "nvs_flash.h"
#include "esp_log.h"

#include "wifi_app.h"
#include "esp_udp_link.h"
#include "drone_control.h"
#include "autonomous_drone_control.h"

#define TAG "Main App"

void app_main(void) {
  // Initialize NVS
  esp_err_t ret = nvs_flash_init();
  if(ret == ESP_ERR_NVS_NO_FREE_PAGES || ret == ESP_ERR_NVS_NEW_VERSION_FOUND) {
    ESP_ERROR_CHECK(nvs_flash_erase());
    ret = nvs_flash_init();
  }
  ESP_ERROR_CHECK(ret);

  ESP_LOGI(TAG, "**************|| Starting WiFi Connection ||**************");
  wifi_app_start();

  ESP_LOGI(TAG, "**************|| Initialize the UDP socket ||**************");
  xTaskCreate(udp_client_task, "udp_client_task", 4096, NULL, 5, NULL);

  // ESP_LOGI(TAG, "**************|| Starting in autonomous mode ||**************");
  // start_autonomous_control();

  // ESP_LOGI(TAG, "**************|| Starting UDP link ||**************");
  // start_drone_control();
}
