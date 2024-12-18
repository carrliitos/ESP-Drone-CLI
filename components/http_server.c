#include "esp_http_server.h"
#include "esp_log.h"
#include "esp_err.h"
#include <stddef.h>

#include "http_server.h"

static const char *TAG = "web_server";

// Handler for the root URL
esp_err_t root_get_handler(httpd_req_t *req) {
  const char *response = "ESP-Drone Web Server";
  httpd_resp_send(req, response, strlen(response));
  return ESP_OK;
}

// URI structure for the root URL
static const httpd_uri_t root = {
  .uri       = "/",
  .method    = HTTP_GET,
  .handler   = root_get_handler,
  .user_ctx  = NULL
};

// Function to start the web server
httpd_handle_t start_webserver(void) {
  httpd_config_t config = HTTPD_DEFAULT_CONFIG();
  httpd_handle_t server = NULL;

  if (httpd_start(&server, &config) == ESP_OK) {
    httpd_register_uri_handler(server, &root);
    ESP_LOGI(TAG, "Web server started successfully");
  } else {
    ESP_LOGE(TAG, "Failed to start web server");
  }
  return server;
}

// Function to stop the web server
void stop_webserver(httpd_handle_t server) {
  if (server) {
    httpd_stop(server);
    ESP_LOGI(TAG, "Web server stopped");
  }
}
