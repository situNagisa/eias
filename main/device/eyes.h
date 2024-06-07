#pragma once

#include "./defined.h"

struct eyes
{
	using serial_type = ::boost::asio::serial_port;

	eyes(serial_type& port)
		: _port(port)
	{
	}

	static void _callback(const ::boost::system::error_code& error, ::std::size_t bytes_transferred)
	{
		if (error)
		{
			NGS_LOGL(error, error.message());
			return;
		}
		NGS_LOGL(info, "set eyes status normal ", bytes_transferred);
	}

	void normal()
	{
		constexpr ::std::string_view command{ "a",1 };
		_port.async_write_some(::boost::asio::buffer(command), _callback);
	}

	void blink()
	{
		constexpr ::std::string_view command{ "b",1 };
		_port.async_write_some(::boost::asio::buffer(command), _callback);
	}

	void star()
	{
		constexpr ::std::string_view command{ "c",1 };
		_port.async_write_some(::boost::asio::buffer(command), _callback);
	}

	void momomo()
	{
		constexpr ::std::string_view command{ "d",1 };
		_port.async_write_some(::boost::asio::buffer(command), _callback);
	}

	serial_type& _port;
};