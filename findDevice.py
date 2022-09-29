import usb.core
import subprocess
import re


def findDevice():
    device_re = re.compile(b"Bus\s+(?P<bus>\d+)\s+Device\s+(?P<device>\d+).+ID\s(?P<id>\w+:\w+)\s(?P<tag>.+)$", re.I)
    df = subprocess.check_output("lsusb")

    devices = []
    for i in df.split(b'\n'):
        if i:
            info = device_re.match(i)
            if info:
                dinfo = info.groupdict()
                dinfo['device'] = '/dev/bus/usb/%s/%s' % (dinfo.pop('bus'), dinfo.pop('device'))
                devices.append(dinfo)

    bus_adr = list()
    for i in range(len(devices)):
        bus_adr.append(devices[i]['device'][15:18] + ":" + devices[i]['device'][22:25])


    device = usb.core.find(find_all=True)

    port_device = dict()
    no_device = 1

    for dev in device:
        if dev.idVendor == 0x04e8 and dev.idProduct == 0x6862:
            no_device = 0

            bus = '{:03d}'.format(dev.bus)
            adr = '{:03d}'.format(dev.address)

            cmd_grep = "grep -l " "{}/{}".format(bus, adr) + " /sys/bus/usb/devices/*/uevent"
            number_of_port = subprocess.check_output(cmd_grep, shell=True).decode()

            for i in range(len(bus_adr)):
                if bus_adr[i] == (bus + ":" + adr):
                    port_device.update({number_of_port[23:24] : [bus + ":" + adr, devices[i]['tag'].decode()]})
            
    return(port_device)
