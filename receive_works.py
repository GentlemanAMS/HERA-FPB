import serial

ser = serial.Serial("/dev/ttyACM0", 115200)
while True:
    b = ser.read(1)
    print(b)
