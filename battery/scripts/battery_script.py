#!/usr/bin/python

# Battery code from @pudquick / Michael Lynn
# https://gist.github.com/pudquick/134acb5f7423312effcc98ec56679136


import os
import sys

import objc
from Foundation import NSBundle
IOKit = NSBundle.bundleWithIdentifier_('com.apple.framework.IOKit')
functions = [("IOServiceGetMatchingService", b"II@"),
             ("IOServiceMatching", b"@*"),
             ("IORegistryEntryCreateCFProperties", b"IIo^@@I"),
             ("IOPSCopyPowerSourcesByType", b"@I"),
             ("IOPSCopyPowerSourcesInfo", b"@"),
            ]
objc.loadBundleFunctions(IOKit, globals(), functions)

sys.path.append("/usr/local/munki/munkilib")
import FoundationPlist


RESULTS_PATH = "/usr/local/sal/plugin_results.plist"


def main():
    data = raw_battery_dict()
    # If this is not a laptop, data will just be empty. No need to do
    # more work.
    if data:
        adjusted_dict = adjusted_battery_dict()
        if adjusted_dict and "BatteryHealth" in adjusted_dict:
            data["BatteryHealth"] = adjusted_dict["BatteryHealth"]
        else:
            data["BatteryHealth"] = "Unkonwn"

    formatted_results = {
        "plugin": "Battery",
        "historical": False,
        "data": data}

    if os.path.exists(RESULTS_PATH):
        plugin_results = FoundationPlist.readPlist(RESULTS_PATH)
    else:
        plugin_results = []

    plugin_results.append(formatted_results)

    FoundationPlist.writePlist(plugin_results, RESULTS_PATH)


def raw_battery_dict():
    # matches information pulled by: pmset -g rawbatt
    battery = IOServiceGetMatchingService(
        0, IOServiceMatching("AppleSmartBattery"))
    if battery != 0:
        err, props = IORegistryEntryCreateCFProperties(
            battery, None, None, 0)
    else:
        props = {}
    return props


def adjusted_battery_dict():
	# matches information pulled by: pmset -g batt
    try:
        battery = list(IOPSCopyPowerSourcesByType(0))[0]
    except:
        battery = 0
    if (battery != 0):
        return battery


if __name__ == "__main__":
    main()