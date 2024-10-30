#include "communication_functions.h"
#include <iostream>
#include <cstring>
#include <unistd.h>
#include <json/json.h>

// Function definitions
int get_socket() {
    const char* socket_path = "/tmp/matrix_connector";
    int client = socket(AF_UNIX, SOCK_STREAM, 0);
    if (client < 0) {
        std::cerr << "Error creating socket" << std::endl;
        exit(1);
    }

    struct sockaddr_un addr;
    memset(&addr, 0, sizeof(addr));
    addr.sun_family = AF_UNIX;
    strncpy(addr.sun_path, socket_path, sizeof(addr.sun_path) - 1);

    if (connect(client, (struct sockaddr*)&addr, sizeof(addr)) < 0) {
        std::cerr << "Error connecting to socket" << std::endl;
        close(client);
        exit(1);
    }

    return client;
}

bool send_message(int client, const std::string& strr) {
    std::string message = strr;
    try {
        std::cout << "Sending message of length: " << message.length() << std::endl;
        std::cout << "Sending message length..." << std::endl;
        uint32_t len = htonl(message.length());
        if (send(client, &len, sizeof(len), 0) < 0) {
            throw std::runtime_error("Error sending message length");
        }

        std::cout << "Sending message..." << std::endl;
        if (send(client, message.c_str(), message.length(), 0) < 0) {
            throw std::runtime_error("Error sending message");
        }
    } catch (const std::exception& e) {
        std::cerr << e.what() << std::endl;
        close(client);
        exit(1);
    }

    char buffer[1024];
    ssize_t bytes_received = recv(client, buffer, sizeof(buffer) - 1, 0);
    if (bytes_received < 0) {
        std::cerr << "Error receiving response" << std::endl;
        close(client);
        exit(1);
    }

    buffer[bytes_received] = '\0';
    Json::Value response;
    Json::CharReaderBuilder reader;
    std::string errs;
    std::istringstream s(buffer);
    if (!Json::parseFromStream(reader, s, &response, &errs)) {
        std::cerr << "Error parsing JSON response: " << errs << std::endl;
        close(client);
        exit(1);
    }

    if (response["success"].asBool()) {
        return true;
    } else {
        throw std::runtime_error("Something bad happened in the matrix connector");
        return false;
    }
}