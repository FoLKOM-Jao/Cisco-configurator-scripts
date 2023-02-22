import re
import serial
from netmiko import ConnectHandler
from decimal import *
import time
import os
import shutil
import difflib
import platform
from netmiko import NetmikoAuthenticationException
# from paramiko.ssh_exception import AuthenticationException
# from difflib import Differ
# import netmiko
# import sys
# from pathlib import Path
# import os.path

i = j = k = l = False


## Gather info ## You can remove comment, and select port manually.
# comport = "COM?"

## Comment out else, if you chose COM port manually.
if platform.system() == "Linux":
    comport = "/dev/ttyUSB0"
else:
    comport = input("With what serial COM port are you connecting (e.g. COM1/com1): ").upper()


filename = input("Name of the config file without format .conf (It's added with code): ").lower()
configfile = filename + ".conf"

def tryconn():
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
    global i
    global m
    m = 0
    while m <= 5:
        try:
            conn = ConnectHandler(**device)
        except NetmikoAuthenticationException:
            #print("Wrong login data, try again.")
            m = m+1
        else:
            print("Password should be correct.")
            i = True
            m = 6

if l == 6:
    print("Wrong login data, try again.")

## Change Auth data ## You can enter UN/PW info here. ##
unAuth = ""
pwAuth = ""

## If you enter auth info manually then comment next section. ##
# """

while i is False:
    changeAuth = input("Do you want to change authentication information? Default is without UN & PW. Yes/No ").lower()
    if changeAuth == "yes" or changeAuth == "no":
        if changeAuth == "yes":
            unAuth = input("Username: ").lower()
            pwAuth = input("Password: ")
            tryconn()
        else:
            tryconn()
    else:
        print("Incorrect entry! Try again.")
# """

## Option to save newly generated files to unique directory ##

prefix_path = os.getcwd()
sign = ""
if platform.system() == "Linux":
    sign = "/"
else:
    sign = "\\"

prefix_path_case = prefix_path + sign + filename

while os.path.exists(prefix_path_case):
    new_filename = filename + str(j)
    prefix_path_case = prefix_path + sign + new_filename
    j = j + 1

os.mkdir(prefix_path_case)
save_files_to = prefix_path_case + sign

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
#if l == 6:
    #print("Wrong login data, try again.")

while l <= 5:
    try:
        ConnectHandler(**device)
    except NetmikoAuthenticationException:
        #print("Wrong login data, try again.")
        l = l+1
    else:
        #conn = ConnectHandler(**device)
        conn = ConnectHandler(**device)
        print("Connected")
        if not conn.check_enable_mode():
            conn.enable()
        l = 6


## Save old config ##
saved_old = filename + "_old.txt"
save_config_to = open(save_files_to + saved_old, "w")
s = conn.send_command_timing("show running-config")
save_config_to.write(s)
save_config_to.close()

## Function for deleting vlan.dat and config ##
def delvlandat():
    conn.send_command("del flash:vlan.dat", expect_string=r'Delete filename')
    conn.send_command("\n", expect_string=r'Delete')
    conn.send_command("\n", expect_string=r'#')


## Function for deleting config ##
def delrunconfig():
    conn.send_command_timing("write erase")
    conn.send_command_timing("\n")
    reload_out = conn.send_command_timing("reload")
    if "Save?" in reload_out:
        conn.send_command_timing("no")

    conn.send_command_timing("\n")
    print("Switch has been reset and restarted.")

## Check and delete vlan.dat file ##
vlandat = ""
vlandatcheck = conn.send_command("dir")
redat = re.search(r'vlan\s*(\S+)', vlandatcheck)

try:
    redat.group()
except AttributeError:
    print("File vlan.dat doesn't exist.")
else:
    vlandat = redat.group()

## If there is no username unAuth is false ##
if unAuth:
    if vlandat == "vlan.dat":
        delvlandat()
        delrunconfig()
    else:
        delrunconfig()
        print("Switch was configured but without vlan.dat file.")
else:
    if vlandat == "vlan.dat":
        delvlandat()
        delrunconfig()
        print("Switch was configured, but without required login.")
    else:
        delrunconfig()
        print("Switch didn't have required login and vlan.dat file.")

conn.disconnect()

## Delay after restart ##
t = time.localtime()
current_time = time.strftime("%H:%M:%S", t)
print("Time of restart is ", current_time)
print("The restart will take around 5 minutes.")
time.sleep(230)

## After reset there is no Auth data ##
unAuth = ""
pwAuth = ""

## Test if switch is already online ##
while k is False:
    try:
        ConnectHandler(**device)
    except NetmikoAuthenticationException:
        time.sleep(30)
    else:
        k = True


## Connect to device & enable ##
print("Connecting...")
conn = ConnectHandler(**device)
print("Connected")
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

## Copy inserted config to case map for easier archiving ##
shutil.copy2(prefix_path + sign + configfile, save_files_to + configfile)

## Save loaded config from the switch for double-checking ##
saved_run = filename + "_running.txt"
saved_dif = filename + "_diference.txt"
save_config_to = open(save_files_to + saved_run, "w")
s = conn.send_command_timing("show running-config")
save_config_to.write(s)
save_config_to.close()
print("Config is copied directly from the switch. You can check it in " + saved_run + ". ")
print("Differences between chosen .conf file and running configuration is saved in: " + saved_dif + ".")
print("All files are saved in a map with the same name as chosen config file.")

with open(save_files_to + configfile) as file_1:
    with open(save_files_to + saved_run) as file_2:
        file_1_line = file_1.readlines()
        file_2_line = file_2.readlines()
        d = difflib.Differ()  # compare and just print
        diff = list(d.compare(file_1_line, file_2_line))
        dif_f = open(save_files_to + saved_dif, "w")
        dif_f.write("\n".join(diff))

dif_f.close()

conn.disconnect()

input()