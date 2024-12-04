/*
 * esp_udp_link.h
 *
 * Created on:         2024-12-02 23:06:19
 *     Author:         carlitos (benzon.salazar@gmail.com)
 *
 * Last Modified by:   carlitos
 * Last Modified time: 2024-12-03 00:13:21
 */

#ifndef MAIN_ESP_UD_LINK_H_
#define MAIN_ESP_UD_LINK_H_

#include <stddef.h>

// Initialize the UDP socket
void udp_link_init(void);

// Send data via UDP
void udp_link_send(const void *data, size_t len);

// Get the current UDP socket descriptor
int get_udp_socket(void);

#endif /* MAIN_ESP_UD_LINK_H_ */