all:
	g++ ./main/main.cpp -I./extern/boost/include -I./extern/websocketpp/include -I./main -I$(NGS_ROOT)/include -o main.out -std=c++23