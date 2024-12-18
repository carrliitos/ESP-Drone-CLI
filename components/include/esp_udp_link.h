#ifndef MAIN_ESP_UDP_LINK_H_
#define MAIN_ESP_UDP_LINK_H_

#include <stddef.h>

// Initialize the UDP socket
void udp_link_init(void);

// Send data via UDP
void udp_link_send(const char *message);

// Receive data via UDP
void udp_link_receive(void);

// Close the UDP socket
void udp_link_close(void);

// Task to send and receive messages
void udp_client_task(void *pvParameters);

#endif /* MAIN_ESP_UDP_LINK_H_ */