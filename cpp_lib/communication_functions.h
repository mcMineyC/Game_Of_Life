#ifndef COMMUNICATION_FUNCTIONS_H
#define COMMUNICATION_FUNCTIONS_H

#include <string>
#include <sys/socket.h>
#include <sys/un.h>

// Function declarations
int get_socket();
bool send_message(int client, const std::string& strr);

#endif // COMMUNICATION_FUNCTIONS_H