#pragma once

#include <websocketpp/config/asio_no_tls_client.hpp>
#include <websocketpp/client.hpp>
#include <boost/property_tree/ptree.hpp>
#include <boost/property_tree/json_parser.hpp>

//#define NGS_USE_HPP
//#include "NGS/basic/basic.h"
//#include "NGS/log/log.h"

#define NGS_LOGL(...) (void*)(nullptr)

#include <filesystem>
#include <chrono>
#include <thread>
