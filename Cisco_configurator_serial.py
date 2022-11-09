import re
import serial
import netmiko
from netmiko import ConnectHandler
from decimal import *
import time

## Gather info ## You can remove comment, and select port manually.
# comport = "COM?"

## Comment next line if you chose COM port manually.
comport = input("With what serial COM port are you connecting (e.g. COM1/com1): ").upper()
filename = input("Name of the config file without format .conf (It's added with code): ").lower()
configfile = filename + ".conf"

## Change Auth data ## You can enter UN/PW info here.
unAuth = ""
pwAuth = ""

## If you enter auth info manually then comment next section.
# """"
i = False
while i == False:
    changeAuth = input("Do you want to change authentication information? Default is without UN & PW. Yes/No ").lower()
    print("If you enter wrong authentication information the script will crash and you will have to start over")
    if changeAuth == "yes" or changeAuth == "no":
        if changeAuth == "yes":
            unAuth = input("Username: ").lower()
            pwAuth = input("Password: ")
            i = True
        else:
            break
    else:
        print("Incorrect entry! Try again.")
# """

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

## Function for deleting vlan.dat and config ##
def delvlandat():
    conn.send_command_timing("del flash:vlan.dat")
    conn.send_command_timing("\n")
    conn.send_command_timing("y")
    conn.send_command_timing("write erase")
    conn.send_command_timing("\n")
    reloadout1 = conn.send_command_timing("reload")
    if "changes" in reloadout1:
        conn.send_command_timing("no")
    else:
        conn.send_command_timing("\n")
    print("Switch has been reset and restarted.")


## Function for deleting config ##
def delrunconfig():
    conn.send_command_timing("write erase")
    conn.send_command_timing("\n")
    reloadout2 = conn.send_command_timing("reload")
    if "changes" in reloadout2:
        conn.send_command_timing("no")
    else:
        conn.send_command_timing("\n")
    print("Switch has been reset and restarted.")


## Check and delete vlan.dat file ##
vlandat = ""
vlandatcheck = conn.send_command("dir")
redat = re.search(r'vlan\s*(\S+)', vlandatcheck)

try:
    vlandat = redat.group()
except AttributeError:
    print("File vlan.dat doesn't exist.")
else:
    vlandat = redat.group()
## If there is no username unAuth is false ##
if unAuth:
    if vlandat == "vlan.dat":
        delvlandat()
    else:
        delrunconfig()
        print("Switch was configured but without vlan.dat file.")
else:
    if vlandat == "vlan.dat":
        delvlandat()
        print("Switch was configured, but without required login.")
    else:
        delrunconfig()
        print("Switch didn't have required login and vlan.dat file.")

conn.disconnect()

## Delay after restart ##
t = time.localtime()
current_time = time.strftime("%H:%M:%S", t)
print("Time of restart is ", current_time)
print("The restart will take 5 minutes.")
time.sleep(300)

## After reset there is no Auth data ##
unAuth = ""
pwAuth = ""

## Connect to device & enable ##
print("Connecting...")
conn = ConnectHandler(**device)
if not conn.check_enable_mode():
    conn.enable()

## When the switch has been reset we need to cancel the first auto setup ##
conn.send_command_timing("\n")
conn.send_command_timing("no")
cmdshver = conn.send_command_timing("show ver")

## Check software version and return answer (Change to the version of IOS you want to have) ##
ios_release = 15.2
ios_version = 6

rever = re.search(r'Version\s*(\S+)[^, ]', cmdshver)
ver = rever.group()
print(ver)

splitver = ver.split("Version ")
splitver2 = splitver[1].split("(")

iosvernum = int(splitver2[1][0])

iosreleasenum = splitver2[0]
iosreleasenum = Decimal(iosreleasenum)

if iosreleasenum < ios_release:
    print("Update software")
else:
    if iosvernum < ios_version:
        print("Update software")
    else:
        print("Software is up to date")

## Connect to device and upload config ##
with open(file=configfile, mode="r") as f:
    config = f.read().splitlines()

conn.send_config_set(config)
conn.send_command_timing("write memory")
print("Config is installed and saved with wr mem.")

## Save loaded config from the switch for double-checking ##
save_config_to = open(filename, "w")
s = conn.send_command_timing("show running-config")
save_config_to.write(s)
save_config_to.close()
print("Config is copied directly from the switch. You can check it in " + filename + ". ")

conn.disconnect()

input()

