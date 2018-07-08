#!/usr/bin/env python3
from PIL import Image
from pathlib import Path
import os, sys, random, time, argparse, configparser

# functions

def splitmonitor(splitstring):
    # split monitor size defs into 2 tuples and converts to int
    splittruple = splitstring.split("x")
    inttruple = (int(splittruple[0]), int(splittruple[1]))
    return inttruple


def comparedimensions(monitorsize, imagesize):
    # figure out the difference between the image height/width and monitor height/width
    # if sizediff > 0 then monitor is wider/higher, if < 0 picture is wider/higher, if 0 then both are equal
    sizediff = 0

    if monitorsize > imagesize:
        sizediff = int((monitorsize - imagesize) / 2)  # how much space we should add either side

    elif monitorsize < imagesize:
        sizediff = monitorsize - imagesize # gives negitive number to resize image by

    return sizediff

def selectrandomfile():
    print ('Selecting random image from')


# main

# variables
debug = True

# todo: need to do something else here and add to ini file
willchopimage = False
willfixedsizeimage = False
willscaleimage = True

configpath = os.path.dirname(str(Path.home()) + "/.config/kbgswitcher/")
configfile = configpath + "/kbswitcher.ini"
config = configparser.ConfigParser()
monitors = [] # list of monitor tuples
totalmonitorwidth = 0
totalmonitorheight = 0
totalmonitorsize = 0
currentwidthoffset = 0
imageslist = []
givenimagefile = ''

print("KBGSwitcher")

# parse command line arg (should be image to split)
parser = argparse.ArgumentParser(description='Splits multimonitor wallpapers and sets them on your KDE desktops.')
arggroup = parser.add_mutually_exclusive_group()
arggroup.add_argument('-r', metavar='/path/to/images/', help='choose a random .png or .jpg from a directory')
arggroup.add_argument('-i', metavar='image.png|.jpg', help='image file to set as the wallpaper')
args = parser.parse_args()


# Check arguments and set our new image up
if args.r:
    print('Trying to select random image...')
    if not os.path.exists(args.r):
        print("Error: " + args.r + " directory not found.")
        sys.exit()
    else:
        givenimagefile = args.r + random.choice(os.listdir(args.r))
        print('Selected ' + givenimagefile)

elif args.i:
    print('Trying to select open specific image...')
    if not os.path.isfile(args.i):
        print("Error: " + args.i + " image not found.")
        sys.exit()
    else:
        givenimagefile = args.i




# Set up variables from config file
if not os.path.exists(configpath):
    os.makedirs(configpath)

if not os.path.isfile(configfile):
    print ("Error: " + configfile + " not found.")
    sys.exit()
else:
    print("Reading config")
    config.read(configfile)

for entry in config['MONITORS']:
    print(config.get('MONITORS', entry))
    monitors.append(splitmonitor(config.get('MONITORS', entry)))

for monitor in monitors:
    totalmonitorwidth += int(monitor[0])
    if int(monitor[1]) > totalmonitorheight:
        totalmonitorheight = int(monitor[1])

totalmonitorsize = (totalmonitorwidth, totalmonitorheight)

#open our given or random image
origimg = Image.open(givenimagefile)

# create a new image that is the size of all the monitors with a black background
newimg = Image.new('RGB', totalmonitorsize)

# figure out the difference between the image width and monitors width / 2
# if sizediff > 0 then monitor is wider/higher, if < 0 picture is wider/higher, if 0 then both are equal
widthsizediff = comparedimensions(totalmonitorwidth, origimg.width)

# figure out the difference between the image height and monitor height / 2
heightsizediff = comparedimensions(totalmonitorheight, origimg.height)

if willscaleimage:
    # todo: scale image instead of just adding black to the top/sides
    print('Creating scaled image...')
    newimg = origimg.resize(totalmonitorsize)  # scales the image to the size of the monitors, but keeps aspect ratio if smaller than monitors

elif widthsizediff < 0 or heightsizediff < 0:   # image height or width GREATER THAN monitor size
    print("image height or width greater than monitor/s")

    if willchopimage:
        print('Chopping image...')
        offsetcoord = (widthsizediff, heightsizediff)
        newimg.paste(origimg, offsetcoord)

    elif willfixedsizeimage:
        print('Creating fixed size image...')
        newimg = origimg.resize(totalmonitorsize) # scales the image to the size of the monitors, but keeps aspect ratio if smaller than monitors

elif widthsizediff > 0 or heightsizediff > 0: # image height or width LESS THAN monitor size
    print("Image height or width smaller than monitor/s")

    offsetcoord = (widthsizediff, heightsizediff)
    newimg.paste(origimg, offsetcoord)

else: # widthsizediff == 0 and heightsizediff == 0  ie: image size == monitors size
    # this may be redundant now..
    print("Image was the same size as the monitor/s")
    newimg.paste(origimg)

newimg.save(configpath + '/tempimg_beforesplit.png')

# split (crop) images up for monitors
print("Splitting images...")

#todo: prob need to check that the image is big enough before splitting as this will probably cause an error

for monitor in monitors:
    splitimg = Image.new('RGB', monitor)
    currentoffsent = currentwidthoffset + monitor[0]  # the X has to be the offset + the monitor in size
    box = (currentwidthoffset, 0, currentoffsent, monitor[1])
    imageslist.append(newimg.crop(box))
    currentwidthoffset = currentoffsent

currentimgnumber = 1  # kde desktops start at 1 then do random shit
for image in imageslist:
    image.save(configpath + '/tempimg_' + str(currentimgnumber) + '.png')
    currentimgnumber += 1;





# save images in correct spot & refresh KDE desktop
# config file is: .config/plasma-org.kde.plasma.desktop-appletsrc

print("Trying to set wallpapers...")


newkdecommand = """
qdbus org.kde.plasmashell /PlasmaShell org.kde.PlasmaShell.evaluateScript '
    var allDesktops = desktops();
    var i = {desktop_number};
    d = desktopById(i);
    d.wallpaperPlugin = "org.kde.image";
    d.currentConfigGroup = Array("Wallpaper", "org.kde.image", "General");
    filestring = "{save_location}";
    d.writeConfig("Image", filestring)
'
"""

saveloc = "file:///" + configpath + "/tempimg_"

# blanking out the current wallpaper so KDE will pick up our changes
# todo: it appears that the file names need to change or KDE will tell you to go fuck yourself
print ('Blanking wallpaper...')

os.system(newkdecommand.format(save_location=configpath + "/blank.png", desktop_number="1"))
os.system(newkdecommand.format(save_location=configpath + "/blank.png", desktop_number="11"))
os.system(newkdecommand.format(save_location=configpath + "/blank.png", desktop_number="12"))

print ('Waiting 5 seconds for kde to catch up..')
time.sleep(5)

print ('Setting wallpaper' )

# note: the below desktop numbers are currently hard coded to what I have in the kde config file :(

# first monitor
os.system(newkdecommand.format(save_location=saveloc + "2.png", desktop_number="1"))


# left monitor
os.system(newkdecommand.format(save_location=saveloc + "1.png", desktop_number="11"))


# right monitor
os.system(newkdecommand.format(save_location=saveloc + "3.png", desktop_number="12"))


print("Should have set wallpaper now.")





