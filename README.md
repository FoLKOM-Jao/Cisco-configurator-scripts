# Cisco-configurator-scripts
Configure one Cisco switch through a serial connection with the already prepared configuration file.


What does the script do:
- Ask for input information.
- Test if Auth info is correct.
- Save currently running configuration to txt file.
- Check if vlan.dat file exists/remove it.
- Remove running configuration (write erase).
- Restart switch.
- Check if the software is uptodate.
- Load new chosen config.
- Save currently running configuration to txt file.
- Compare chosen config to that which is currently running (to check for mistakes).

All of these files that are saved, are located in a uniquely named folder.

# Input
After running the script, you will have to input some information:
- Which COM port is used,
- The name of the config file,
- Authentication information if needed.
