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
		: _eyes(_io, eyes_device)
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

	::boost::asio::io_service _io{};
	client_type _client{};
	eyes _eyes;
	//steering_engine _steering;
};