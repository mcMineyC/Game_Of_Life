#include <iostream>
#include <stdio.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <unistd.h>
#include <string.h>
#include <signal.h>
#include <exception>
#include <math.h>
#include <arpa/inet.h>
#include <vector>
#include <sstream>

#define SOCKET_PATH "/tmp/matrix_connector"
using namespace std;


bool pi = false;

volatile bool interrupt_received = false;
static void InterruptHandler(int signo) {
  interrupt_received = true;
}

class ScrewyError : public std::exception {
public:
    const char* what() const throw() {
        return "Summin' screwy happn'd 'ere";
    }
};


std::vector<std::string> splitString(const std::string& str) {
    std::vector<std::string> lines;
    if (str.empty()) {
        return lines;
    }

    std::istringstream iss(str);
    std::string line;

    while (std::getline(iss, line)) {
        lines.push_back(line);
    }
    return lines;
}

int main(int argc, char* argv[]) {
    // signal(SIGTERM, InterruptHandler);
    // signal(SIGINT, InterruptHandler);

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
    cl = accept(fd, NULL, NULL);
    if (cl == -1) {
        std::cerr << "accept error" << std::endl;
        exit(-1);
    }else{
        std::cout << "Got connection\n";
    }
    while (true) {
        std::cout << "Server is listening for incoming connections..." << std::endl;

        uint32_t length;
        if (read(cl, &length, sizeof(length)) != sizeof(length)) {
            std::cerr << "read error";
            exit(1);
        }
        length = ntohl(length);
        std::cout << "Expecting message of length: " << length << std::endl;

        std::string total_data;
        total_data.resize(length);
        char* buf = &total_data[0];
        size_t total_read = 0;
        ssize_t rc = read(cl, buf + total_read, length - total_read);
        std::cout << "read " << rc << " bytes\n";
        total_read += rc;

        std::cout << "Readed " << total_read << " bytes\n";
        if(total_read == length){
            rc = 0;
        }else if(total_read < length){
            rc = -1;
        }else if(total_read > length){
            throw ScrewyError();
            exit(1);
        }
        if (rc == -1) {
            cerr << endl << "read error, expected " << length << " bytes, got " << total_read << " bytes\n";
            // exit(1);
        }else if (rc == 0) {
            cout << "All done\trc: " << rc << "\nRead in:\n" << total_data << "\nSize: "<< total_data.size() <<"\n";
            string now = total_data;
            std::vector<string> lines = splitString(now);
            for(size_t y = 0; y < lines.size(); y++){
                string line = lines[y];
                if(!pi) cout << line << endl;
                for(size_t x = 0; x < line.size(); x++){
                    // cout << line[x];
                }
            }
            cout << "Image received" << endl;
            cout << endl;
            string response = "{\"success\":true}";
            send(cl, response.c_str(), response.size(), 0);
            // close(cl);
        }
    }

    return 0;
}