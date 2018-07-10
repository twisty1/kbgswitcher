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


# main
if __name__ == '__main__':

    # variables
    debug = True
    scaleimage = 0;
    configpath = os.path.dirname(str(Path.home()) + "/.config/kbgswitcher/")
    configfile = configpath + "/kbswitcher.ini"
    blankimage = configpath + "/blank.png"
    config = configparser.ConfigParser()
    monitors = [] # list of monitor tuples
    totalmonitorwidth = 0
    totalmonitorheight = 0
    totalmonitorsize = 0
    currentwidthoffset = 0
    imageslist = []
    givenimagefile = ''

    print("KBGSwitcher")


    # Check if config file exists
    # Set up variables from config file
    if not os.path.exists(configpath):
        os.makedirs(configpath)

    if not os.path.isfile(configfile):
        print("kbgswitcher: error: " + configfile + " was not found but was created.")
        print("Please see the man page for details on how to modify it and configure KBGswitcher")
        newconfigfile = open(configfile, "w+")
        newconfigtext = "[LIST]\nmonitors = 1\n\n[MONITORS]\nmonitor0 = 1920x1080\n\n[CONTAINMENTS]\nmonitor0 = 1\n\n[GENERAL]\nscaleimage = 0"
        newconfigfile.writelines(newconfigtext)
        sys.exit()
    else:
        config.read(configfile)

    # check if blank.png exists, create it progmatically if not
    if not os.path.isfile(blankimage):
        print("creating blank image")
        img = Image.new('RGB', (1920, 1080), color='black')
        img.save(blankimage)


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
            print("kbgswitcher: error: " + args.r + " directory not found.")
            sys.exit()
        else:
            givenimagefile = args.r + random.choice(os.listdir(args.r))
            print('Selected ' + givenimagefile)

    elif args.i:
        print('Trying to select open specific image...')
        if not os.path.isfile(args.i):
            print("kbgswitcher: error: " + args.i + " image not found.")
            sys.exit()
        else:
            givenimagefile = args.i
    else:
        print ("usage: kbgswitcher.py [-h] [-r /path/to/images/ | -i image.png|.jpg]")
        print("kbgswitcher: error: no arguments given. Please see -h for help.")
        sys.exit()

    for entry in config['MONITORS']:
        print(config.get('MONITORS', entry))
        monitors.append(splitmonitor(config.get('MONITORS', entry)))

    for monitor in monitors:
        totalmonitorwidth += int(monitor[0])
        if int(monitor[1]) > totalmonitorheight:
            totalmonitorheight = int(monitor[1])

    # scaleimage - 0=scale, 1 = chop, 2=fixed
    scaleimage = int(config.get('GENERAL', 'scaleimage'))

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

    if scaleimage == 0:
        print('Creating scaled image...')
        newimg = origimg.resize(totalmonitorsize)  # scales the image to the size of the monitors, but keeps aspect ratio if smaller than monitors

    elif widthsizediff < 0 or heightsizediff < 0:   # image height or width GREATER THAN monitor size
        print("image height or width greater than monitor/s")

        if scaleimage == 1:
            print('Chopping image...')
            offsetcoord = (widthsizediff, heightsizediff)
            newimg.paste(origimg, offsetcoord)

        elif scaleimage == 2:
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
    print ('Blanking wallpaper...')
    for cont, value in config['CONTAINMENTS'].items():
        print ("Blanking containment: " + value)
        os.system(newkdecommand.format(save_location=configpath + "/blank.png", desktop_number= value))



    print ('Waiting 1 second for kde to catch up..')
    time.sleep(1)

    print ('Setting wallpaper' )


    wallpapercounter = 1
    for cont, value in config['CONTAINMENTS'].items():
        print ("Setting containment: " + value)
        os.system(newkdecommand.format(save_location=saveloc + str(wallpapercounter) + ".png", desktop_number= value))
        wallpapercounter += 1

    print("Should have set wallpaper now.")





