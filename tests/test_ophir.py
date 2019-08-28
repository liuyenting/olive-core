from serial import Serial

ser = Serial(port="COM5", baudrate=38400, timeout=1, write_timeout=1)
ser.write(b"$SX\r")
data = ser.read_until("\r").decode("utf-8", errors='backslashreplace')
print(data)
