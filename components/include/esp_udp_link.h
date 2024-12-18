/*
 * esp_udp_link.h
 *
 * Created on:         2024-12-02 23:06:19
 *     Author:         carlitos (benzon.salazar@gmail.com)
 *
 * Last Modified by:   carrliitos
 * Last Modified time: 2024-12-07 20:17:31
 */

#ifndef MAIN_ESP_UDP_LINK_H_
#define MAIN_ESP_UDP_LINK_H_

#include <stddef.h>

// Initialize the UDP socket
void udp_link_init(void);

// Receive data via UDP
void udp_link_receive(void);

// Close the UDP socket
void udp_link_close(void);

// Get the current UDP socket descriptor
int get_udp_socket(void);

#endif /* MAIN_ESP_UDP_LINK_H_ */