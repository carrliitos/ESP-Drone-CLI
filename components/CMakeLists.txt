idf_component_register(
    SRCS "autonomous_drone_control.c"
         "drone_control.c"
         "esp_udp_link.c"
         "http_server.c"
         "wifi_app.c"
    INCLUDE_DIRS "include"
    REQUIRES esp_system esp_wifi esp_event nvs_flash esp_http_server
)
