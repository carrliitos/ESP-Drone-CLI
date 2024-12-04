/*
 * http_server.h
 *
 * Created on:         2024-12-02 16:07:48
 *     Author:         carlitos (benzon.salazar@gmail.com)
 *
 * Last Modified by:   carrliitos
 * Last Modified time: 2024-12-03 18:18:39
 */

#ifndef MAIN_HTTP_SERVER_H_
#define MAIN_HTTP_SERVER_H_

#include "esp_http_server.h"
#include "esp_err.h"
#include <stddef.h>

// Function to start the web server
httpd_handle_t start_webserver(void);

// Function to stop the web server
void stop_webserver(httpd_handle_t server);

// Function to handle root URI
esp_err_t root_get_handler(httpd_req_t *req);

#endif /* MAIN_HTTP_SERVER_H_ */