#include <iostream>
#include <sys/socket.h>
#include <sys/un.h>
#include <unistd.h>
#include <string.h>
#include <json/json.h>

#define SOCKET_PATH "/tmp/matrix_connector"

class ScrewyError : public std::exception {
public:
    const char* what() const throw() {
        return "Summin' screwy happn'd 'ere";
    }
};

int main(int argc, char* argv[]) {
    struct sockaddr_un addr;
    char buf[1024];
    int fd, cl, rc;

    for(int i = 0; i < argc; i++) {
        std::cout << argv[i] << std::endl;
    }

    if ((fd = socket(AF_UNIX, SOCK_STREAM, 0)) == -1) {
        std::cerr << "socket error" << std::endl;
        exit(-1);
    }

    memset(&addr, 0, sizeof(addr));
    addr.sun_family = AF_UNIX;
    strncpy(addr.sun_path, SOCKET_PATH, sizeof(addr.sun_path)-1);
    unlink(SOCKET_PATH);

    if (bind(fd, (struct sockaddr*)&addr, sizeof(addr)) == -1) {
        std::cerr << "bind error" << std::endl;
        exit(-1);
    }

    if (listen(fd, 1) == -1) {
        std::cerr << "listen error" << std::endl;
        exit(-1);
    }

    while (true) {
        std::cout << "Server is listening for incoming connections..." << std::endl;

        if ((cl = accept(fd, NULL, NULL)) == -1) {
            std::cerr << "accept error" << std::endl;
            continue;
        }

        while ((rc = read(cl, buf, sizeof(buf))) > 0) {
            // Process the received data
            // Save the image or display it on the matrix
            // Send a response back to the client
            Json::Value root;
            root["success"] = true;
            Json::StreamWriterBuilder writer;
            std::string response = Json::writeString(writer, root);
            send(cl, response.c_str(), response.size(), 0);
        }
        if (rc == -1) {
            std::cerr << "read error" << std::endl;
            exit(-1);
        }
        else if (rc == 0) {
            std::cout << "EOF" << std::endl;
            close(cl);
        }
    }

    return 0;
}