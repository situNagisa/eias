#include "./application.h"

struct config
{
	::std::string uri{ "ws://localhost:9000" };
	::std::string eyes_device{ "/dev/tyy0" };
	::std::string steering_device{ "/dev/tyy1" };

	void read_from(::std::string_view file)
	{
		::std::ifstream config_file(file.data());
		::boost::property_tree::ptree pt{};

		try
		{
			::boost::property_tree::read_json(config_file, pt);
		}
		catch (const ::boost::property_tree::json_parser_error& e)
		{
			NGS_LOGL(error, e.what());
			return;
		}
		catch (const ::boost::property_tree::ptree_error& e)
		{
			NGS_LOGL(error, e.what());
			return;
		}

		uri = pt.get<::std::string>("uri", "");
		eyes_device = pt.get<::std::string>("eyes_device", "/dev/tyy0");
		steering_device = pt.get<::std::string>("steering_device", "/dev/tyy1");
	}
};


int main()
{
	::boost::asio::io_service io{};
	auto ptr = check_eyes(io, "COM4");
	::std::cout << ::std::boolalpha << (ptr != nullptr) << ::std::endl;
	while (true);
	return 0;
	config config{};
	config.read_from("config.json");

	application app{ config.uri, config.eyes_device, config.steering_device };

	app.run();

	return 0;
}