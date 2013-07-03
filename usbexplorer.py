#!/usr/bin/python

import usb.core
import urllib

URL_LINUXUSB_VID_PID = 'http://www.linux-usb.org/usb.ids'
HEX_CHAR = '0123456789abcdef'

def is_hex(string):
    for char in string:
        if char not in HEX_CHAR:
            return False
    
    return True


def init_vid_pid():

    print('Downloading USB description from linux-USB ... '),
    try:
        ufile = urllib.urlopen(URL_LINUXUSB_VID_PID)
    except URLError:
        print('Can''t open linux-usb.org URL')    
    print('DONE')
    
    print('Generating data internal table ... '),    
    vid_pid_dict = {}
    mode = ''
    
    for line in ufile.readlines():
        if is_hex(line[0:4]):
            vid = int(line[0:4], 16)
            vid_desc = line[6:-1]
            mode = 'VID'
            continue
        
        if line[0] == '\t':
            if vid:
                pid = int(line[1:5], 16)
                pid_desc = line[7:-1]
                vid_pid_dict[(vid, pid)] = (vid_desc, pid_desc)
                continue
            
        vid = ''
    print('DONE')    
                             
    return vid_pid_dict

def init_usb_class():
# Load a map with USB class usage and description
    ldev_class = {}
    ldev_class[0x00] = ('device', 'unspecified')
    ldev_class[0x02] = ('both', 'communications and CDC control')
    ldev_class[0x09] = ('device', 'USB hub')
    ldev_class[0x08] = ('interface', 'mass storage')
    ldev_class[0x0e] = ('interface', 'video')
    ldev_class[0xef] = ('both', 'miscellaneous')
    ldev_class[0xff] = ('both', 'vendor-specific')
    return ldev_class

def describe_ep(lep):

    print('\t\t' + 'End point: %s - attributes: %s'
        % (hex(lep.bEndpointAddress), bin(lep.bmAttributes)))

    return

def describe_intf(lintf, usb_class):

    print('\t' + 'Interface: %i - alter. set.: %i - class: 0x%0.2x' 
        % (lintf.bInterfaceNumber, 
        lintf.bAlternateSetting, lintf.bInterfaceClass)),    
    if lintf.bInterfaceClass in usb_class:
        (lintf_class_usage, lintf_class_description) = usb_class[
            lintf.bInterfaceClass]
        print(lintf_class_description[:25])
    else:
        print('not found')
    for ep in lintf:
        describe_ep(ep)

    return

def describe_cfg(lcfg, usb_class):
    print('Configuration: %i' % lcfg.bConfigurationValue)
    for intf in lcfg:
        describe_intf(intf, usb_class)
    return

def describe_dev(ldev, vid_pid, usb_class):
    if (ldev.idVendor, ldev.idProduct) in vid_pid:
        (vid_desc, pid_desc) = vid_pid[(ldev.idVendor, ldev.idProduct)]
    else:
        vid_desc = 'Not found'
        pid_desc = 'Not found'

    print('Vendor:  0x%0.4x ' % ldev.idVendor + vid_desc)
    print('Product: 0x%0.4x ' % ldev.idProduct + pid_desc)
    print('Bus: %03i:%03i -' % (ldev.bus, ldev.address)),
    print('class: 0x%0.2x ' % ldev.bDeviceClass),
    if ldev.bDeviceClass in usb_class:
        (ldev_class_usage, ldev_class_description) = usb_class[
            ldev.bDeviceClass]
        print(ldev_class_usage + ' ' + ldev_class_description)
    else:
        print('description not found')
    for cfg in ldev:
        describe_cfg(cfg, usb_class)

    return

# Define a main() function 
def main():
    # Initialisation
    vid_pid = init_vid_pid()
    usb_class = init_usb_class()

    devs = usb.core.find(find_all=True)
    print('Total number of devices: %i' % len(devs))
    print
    for dev in devs:
        describe_dev(dev, vid_pid, usb_class)
        print

# This is the standard boilerplate that calls the main() function.
if __name__ == '__main__':
    main()
  



