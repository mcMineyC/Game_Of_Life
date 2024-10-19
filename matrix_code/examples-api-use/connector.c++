#include <iostream>
#include <stdio.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <unistd.h>
#include <string.h>
#include <json/json.h>
#include "led-matrix.h"
#include <signal.h>
#include <exception>
#include <math.h>
#include <arpa/inet.h>
#include <vector>
#include <sstream>

#define SOCKET_PATH "/tmp/matrix_connector"

using rgb_matrix::Canvas;
using rgb_matrix::RGBMatrix;
using rgb_matrix::FrameCanvas;
using namespace std;


bool pi = true;
bool verbose = false;

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


vector<string> splitString(const string& str) {
    std::istringstream iss(str);
    vector<string> lines;
    string line;

    while (std::getline(iss, line)) {
        lines.push_back(line);
    }
    return lines;
}

int main(int argc, char* argv[]) {
    RGBMatrix::Options matrix_options;
    rgb_matrix::RuntimeOptions runtime_opt;
    if (!rgb_matrix::ParseOptionsFromFlags(&argc, &argv,
                                         &matrix_options, &runtime_opt)) {
        if(verbose) cerr << "Error parsing options" << endl;
    }

    // signal(SIGTERM, InterruptHandler);
    // signal(SIGINT, InterruptHandler);

    struct sockaddr_un addr;
    char buf[1024];
    int fd, cl, rc;

    for(int i = 0; i < argc; i++) {
        cout << argv[i] << endl;
    }

    if ((fd = socket(AF_UNIX, SOCK_STREAM, 0)) == -1) {
        cerr << "socket error" << endl;
        exit(-1);
    }

    memset(&addr, 0, sizeof(addr));
    addr.sun_family = AF_UNIX;
    strncpy(addr.sun_path, SOCKET_PATH, sizeof(addr.sun_path)-1);
    unlink(SOCKET_PATH);

    if (bind(fd, (struct sockaddr*)&addr, sizeof(addr)) == -1) {
        cerr << "bind error" << endl;
        exit(-1);
    }

    if (listen(fd, 1) == -1) {
        cerr << "listen error" << endl;
        exit(-1);
    }
    FrameCanvas *canvas;
    RGBMatrix *matrix;
    if(pi){
        matrix = RGBMatrix::CreateFromOptions(matrix_options, runtime_opt);
        canvas = matrix->CreateFrameCanvas();
    }
    cl = accept(fd, NULL, NULL);
    if (cl == -1) {
        if(verbose) cerr << "accept error" << std::endl;
        exit(-1);
    }else{
        if(verbose) cout << "Got connection\n";
    }
    cout << "Server is listening for incoming connections..." << endl;
    while (true) {
        uint32_t length;
        if (read(cl, &length, sizeof(length)) != sizeof(length)) {
            if(verbose) cerr << "read error";
            exit(1);
        }
        length = ntohl(length);
        if(verbose) cout << "Expecting message of length: " << length << endl;

        string total_data;
        total_data.resize(length);
        char* buf = &total_data[0];
        size_t total_read = 0;
        ssize_t rc = read(cl, buf + total_read, length - total_read);
        if(verbose) cout << "read " << rc << " bytes\n";
        total_read += rc;

        if(verbose) cout << "Readed " << total_read << " bytes\n";
        if(total_read == length){
            rc = 0;
        }else if(total_read < length){
            rc = -1;
        }else if(total_read > length){
            throw ScrewyError();
            exit(1);
        }
        if (rc == -1) {
            if(verbose) cerr << endl << "read error, expected " << length << " bytes, got " << total_read << " bytes\n";
            // exit(1);
        }else if (rc == 0) {
            if(verbose) cout << "All done\trc: " << rc << "\nRead in:\n" << total_data << "\nSize: "<< total_data.size() <<"\n";
            string now = total_data;
            vector lines = splitString(now);
            for(size_t y = 0; y < lines.size(); y++){
                string line = lines[y];
                if(!pi && verbose) cout << line << endl;
                for(size_t x = 0; x < line.size(); x++){
                    // cout << line[x];
                    if(pi){
                        int res = line[x] == '0' ? 0 : 255;
                        //              x   y  red green blue
                        canvas->SetPixel(x, y, res, res, res);
                    }
                }
            }

            if(pi){
                canvas = matrix->SwapOnVSync(canvas);
            }
            if(verbose) cout << "Image received" << endl;
            if(verbose) cout << endl;
            Json::Value root;
            root["success"] = true;
            Json::StreamWriterBuilder writer;
            string response = Json::writeString(writer, root);
            send(cl, response.c_str(), response.size(), 0);
            // close(cl);
        }
    }

    return 0;
}
