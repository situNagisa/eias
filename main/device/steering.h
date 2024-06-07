#pragma once

#include "./defined.h"

struct steering_engine
{
	//NGS_PP_INJECT_BEGIN(steering_engine);
public:
	enum class command_type : ::std::uint8_t
	{
		servo_move = 0x03,
	};
	using serial_type = ::boost::asio::serial_port;

	steering_engine(::boost::asio::io_service& io, ::std::string_view device)
		: _port(io, device.data())
	{
		_port.set_option(::boost::asio::serial_port::baud_rate(115200));
		_port.set_option(::boost::asio::serial_port::flow_control(::boost::asio::serial_port::flow_control::none));
		_port.set_option(::boost::asio::serial_port::parity(::boost::asio::serial_port::parity::none));
		_port.set_option(::boost::asio::serial_port::stop_bits(::boost::asio::serial_port::stop_bits::one));
		_port.set_option(::boost::asio::serial_port::character_size(8));
	}

	static void _callback(const ::boost::system::error_code& error, ::std::size_t bytes_transferred)
	{
		if (error)
		{
			NGS_LOGL(error, error.message());
			return;
		}
		NGS_LOGL(info, "data ", bytes_transferred);
	}
	/*
	void _send_command(::std::ranges::contiguous_range auto&& buffer)
	{
		_port.async_write_some(::boost::asio::buffer(NGS_PP_PERFECT_FORWARD(buffer)), [buffer_size = ::std::ranges::size(buffer)](const ::boost::system::error_code& error_code, ::std::size_t bytes_transferred)
			{
				if (error_code)
				{
					NGS_LOGL(error, error_code.message());
					return;
				}
				NGS_LOGL(info, ::std::format("buffer size {}, send {}", buffer_size, bytes_transferred));
			});
	}

	template<command_type Command>
	constexpr auto _create_send_buffer(::std::ranges::input_range auto&& data)
	{
		::std::vector<::std::uint8_t> buffer(4 + ::std::ranges::size(data));
		buffer[0] = 0x55;
		buffer[1] = 0x55;
		buffer[2] = 2 + ::std::ranges::size(data);
		buffer[3] = static_cast<::std::uint8_t>(Command);
		::std::ranges::copy(NGS_PP_PERFECT_FORWARD(data), ::std::ranges::next(::std::ranges::begin(buffer), 4));

		return buffer;
	}

	struct steering_angle
	{
		::std::uint8_t id;
		::std::uint16_t degree;
	};

	void _servo_move(::std::uint16_t time_ms, ::std::ranges::input_range auto&& params)
		requires ::std::convertible_to<::std::ranges::range_value_t<decltype(params)>, steering_angle>
	{
		::std::vector<::std::uint8_t> data(3 + ::std::ranges::size(params) * 3);

		data[0] = ::std::ranges::size(params);
		data[1] = time_ms & 0xff;
		data[2] = (time_ms >> 8) & 0xff;

		for(auto&&[index, param] : params | ::std::views::enumerate)
		{
			data[3 + index * 3 + 0] = static_cast<steering_angle>(param).id;
			data[3 + index * 3 + 1] = static_cast<steering_angle>(param).degree & 0xff;
			data[3 + index * 3 + 2] = (static_cast<steering_angle>(param).degree >> 8) & 0xff;
		}

		_send_command(_create_send_buffer<command_type::servo_move>(::std::move(data)));
	}
	
	void raise_hand(::std::convertible_to<::std::uint8_t> auto... id)
	{
		self_type::_servo_move(1000, ::std::array{ steering_angle{ id, 0 }... } );
	}
	*/
	serial_type _port;
};