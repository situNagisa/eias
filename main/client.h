#pragma once

#include "./defined.h"

struct client
{
	using client_type = ::websocketpp::client<::websocketpp::config::asio_client>;

	struct message_type
	{
		::std::string name{};
		int age{};
		::std::string city{};
	};

	client(::std::function<void(const message_type& message)> callback)
	{
		_client.set_access_channels(::websocketpp::log::alevel::all);
		_client.clear_access_channels(::websocketpp::log::alevel::frame_payload);

		::websocketpp::lib::error_code error;
		_client.init_asio(error);

		if(error)
		{
			NGS_LOGL(error, ::std::format("fail to init asio: {}", error.message()));
			return;
		}

		_client.set_message_handler([callback=::std::move(callback)](::websocketpp::connection_hdl handle, client_type::message_ptr message)
			{
				auto&& json = message->get_payload();

				::std::stringstream ss(json);
				::boost::property_tree::ptree pt{};

				::boost::property_tree::read_json(ss, pt);

				auto&& name = pt.get<::std::string>("name");
				int age = pt.get<int>("age");
				auto&& city = pt.get<::std::string>("city");

				callback({ name, age, city });
			});

	}

	bool try_connect(::std::string_view uri)
	{
		::websocketpp::lib::error_code error;
		auto connection = _client.get_connection(uri.data(), error);

		if (error)
		{
			NGS_LOGL(error, ::std::format("fail to connect {}: {}", uri, error.message()));
			return false;
		}

		// Note that connect really just schedules the connection. It doesn't
		// actually complete until the event loop starts running.
		_client.connect(connection);

		return true;
	}

	void send(::std::string_view message)
	{
		try
		{
			_client.send(_handle, ::std::string{ message }, websocketpp::frame::opcode::text);
		}
		catch (const ::websocketpp::exception& error)
		{
			NGS_LOGL(error, error.what());
		}
		
	}

	auto&& get_client()
	{
		return _client;
	}

	client_type _client{};
	::websocketpp::connection_hdl _handle;
};