import serial
import netmiko
from netmiko import ConnectHandler

## Gather info ## You can remove comment, and select port manually.
#comport = "COM3"
comport = input("With what serial COM port are you connecting (e.g. COM1/com1): ").upper() ## Comment this if you chose COM port manuall.
filename = input("Name of the config file without format .conf (It's added with code): ").lower()
configfile = filename + ".conf"

## Change Auth data ## You can enter UN/PW info here.
unAuth = ""
pwAuth = ""

## If you enter auth info manually then comment next section.
#""""
i = False
while i == False:
    changeAuth = input("Do you want to change authentication information? Default is without UN & PW. Yes/No ").lower()
    print("If you enter wrong authentication information the script will crash.")
    if changeAuth == "yes" or changeAuth == "no":
        if changeAuth == "yes":
            unAuth = input("User name: ").lower()
            pwAuth = input("Password: ")
            i = True
        else:
            break
    else:
        print("Incorrect entry! Try again.")
#"""

## Device info for connection ##
device = {
    "device_type": "cisco_ios_serial",
    "username": unAuth,
    "password": pwAuth,
    "secret": "cisco",
    "fast_cli": False,
    "conn_timeout": 30.0,
    "serial_settings": {
        "baudrate": serial.Serial.BAUDRATES[12],  # 9600
        "bytesize": serial.EIGHTBITS,
        "parity": serial.PARITY_NONE,
        "stopbits": serial.STOPBITS_ONE,
        "port": comport,
    },
}

## Connect to device & enable ##
print("Connecting...")
conn = ConnectHandler(**device)
print("Connected")
if not conn.check_enable_mode():
        conn.enable()

## Chosen config file ##
with open(file= configfile, mode="r") as f:
    config = f.read().splitlines()

## Configuration of device ##
print("Configuring")
conn.send_config_set(config)
conn.send_command_timing("write memory")
print("Config is installed and saved with wr mem.")
conn.disconnect()
