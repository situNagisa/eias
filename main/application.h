#pragma once

#include "./device.h"
#include "./defined.h"

struct application
{
	using client_type = ::websocketpp::client<::websocketpp::config::asio_client>;

	struct message_type
	{
		::std::string topic{};
		::std::string message{};
	};

	application(::std::string_view uri, ::std::string_view eyes_device, ::std::string_view steering_device)
		: _eyes_ptr(_create_eyes_ptr(eyes_device))
		, _eyes(*_eyes_ptr)
		//, _steering(_io, steering_device)
	{
		_client.set_access_channels(::websocketpp::log::alevel::all);
		_client.clear_access_channels(::websocketpp::log::alevel::frame_payload);

		::websocketpp::lib::error_code error;
		_client.init_asio(error);

		if (error)
		{
			NGS_LOGL(error, ::std::format("fail to init asio: {}", error.message()));
			return;
		}

		_client.set_message_handler([this](::websocketpp::connection_hdl handle, client_type::message_ptr message)
			{
				auto&& json = message->get_payload();

				::std::stringstream ss(json);
				::boost::property_tree::ptree pt{};

				::boost::property_tree::read_json(ss, pt);

				_on_message({ pt.get<::std::string>("topic"),pt.get<::std::string>("msg") });
			});
		_client.set_open_handler([this](::websocketpp::connection_hdl handle)
			{
				NGS_LOGL(info, "opened");
				::websocketpp::lib::error_code error;
				_client.send(handle, "hello world", ::websocketpp::frame::opcode::text, error);
				if (error)
				{
					NGS_LOGL(error, ::std::format("fail to send data: {}", error.message()));
				}
			});

		auto connection = _client.get_connection(uri.data(), error);

		if (error)
		{
			NGS_LOGL(error, ::std::format("fail to connect {}: {}", uri, error.message()));
			return;
		}

		// Note that connect really just schedules the connection. It doesn't
		// actually complete until the event loop starts running.
		_client.connect(connection);
	}

	void _on_message(const message_type& message)
	{
		NGS_LOGL(info, ::std::format("topic: {}, message: {}", message.topic, message.message));

		if(message.topic == "eye")
		{
			if (message.message == "normal")
			{
				_eyes.normal();
			}                                                                                                                                                                                                          
			else if (message.message == "blink")
			{
				_eyes.blink();
			}
			else if (message.message == "star")
			{
				_eyes.star();
			}
			else if (message.message == "momomo")
			{
				_eyes.momomo();
			}
		}
	}

	void run()
	{
		while(true)
		{
			try
			{
				_client.poll();
				_io.poll();
			}
			catch (const ::websocketpp::exception& error)
			{
				NGS_LOGL(error, error.what());
			}
			catch (const ::boost::property_tree::json_parser_error& e)
			{
				NGS_LOGL(error, e.what());
				return;
			}
		}
	}


	auto _check_eyes(::std::string_view device) {
		using namespace ::std::chrono_literals;

		::std::unique_ptr<::boost::asio::serial_port> result = nullptr;
		try
		{
			result = ::std::make_unique<::boost::asio::serial_port>(_io, device.data());
			auto&& port = *result;

			port.set_option(::boost::asio::serial_port::baud_rate(115200));
			port.set_option(::boost::asio::serial_port::flow_control(::boost::asio::serial_port::flow_control::none));
			port.set_option(::boost::asio::serial_port::parity(::boost::asio::serial_port::parity::none));
			port.set_option(::boost::asio::serial_port::stop_bits(::boost::asio::serial_port::stop_bits::one));
			port.set_option(::boost::asio::serial_port::character_size(8));

			bool success = false;
			::std::array<::std::uint8_t, 1> receive{};

			port.write_some(::boost::asio::buffer(::std::array<::std::uint8_t, 1>{'n'}));
			port.read_some(::boost::asio::buffer(receive));
			success = (receive[0] == '6');

			if (!success)
				result.reset();

			return result;
		}
		catch (const ::boost::system::system_error& error)
		{
			result.reset();
			return result;
		}
	}

	auto _check_directory(const ::std::filesystem::path& dir)
	{
		::std::unique_ptr<::boost::asio::serial_port> result = nullptr;
		if (!::std::filesystem::is_directory(dir))
			return result;
		if (!::std::filesystem::exists(dir))
			return result;

		for (auto& entry : ::std::filesystem::directory_iterator(dir)) {
			if (::std::filesystem::is_directory(entry.path()))
				continue;
			result = _check_eyes(entry.path().string());
			if (result != nullptr)
				return result;
		}
		return result;
	}

	auto _create_eyes_ptr(::std::string_view device)
	{
		auto result = _check_eyes(device);
		if (result != nullptr)
			return result;
		result = _check_directory("/dev/");
		if (result != nullptr)
			return result;
		return result;
	}

	::boost::asio::io_service _io{};
	::std::unique_ptr<::boost::asio::serial_port> _eyes_ptr;
	client_type _client{};
	eyes _eyes;
	//steering_engine _steering;
};