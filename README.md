# kbgswitcher
Command line utility for switching multi-desktop wallpapers in KDE Plasma 5


## How to Use

1. Run kbswitcher.py. This will set up the necessary directors and a config file under ~/.config/kbgswitcher/kbgswitcher.ini

2. Edit kbgswitcher.ini

3. Run kbgswitcher.py with the arguments you want to set your wallpaper. More information on this can be gotten by using the -h argument. This setup allows you to use kbgswitcher.py in a startup script or in other ways to set a specific or random wallpaper from a folder as you desire.

## How to Configure

The configuration file kbgswitcher.ini contains 4 sections:

### [LIST]
This section contains a single option called 'monitors'. Set this to the number of monitors that you have.

### [MONITORS]
This section contains the dimensions of each monitor that you have. For example:

monitor0 = 1920x1080
monitor1 = 1920x1080
monitor2 = 1920x1080

This usually goes left to right but that all depends on the next section.

### [CONTAINMENTS]
This section is a bit of a pain to configure and may take a bit of trial and error to get right. KDE stores it's desktop settings in a file called '.config/plasma-org.kde.plasma.desktop-appletsrc' and this file contains a "containment" for various different things including your desktops themselves as well as other entities including widgets. It's your job to figure out which containment belongs to each monitor (p.s. if anyone knows of a more exact way to determine this info please let me know).

For example with my 3 monitors I have:

 [CONTAINMENTS]
 monitor0 = 11
 monitor1 = 1
 monitor2 = 12

As you will notice, my left monitor is containment 11, my middle monitor is containment 1 and my right monitor is containment 12. Although this appears neat for me, others have reported all kinds of random numbers that identify each monitor.


### [GENERAL]
This section contains a single option called 'scaleimage'. Kbgswitcher has the ability to either scale your image to your monitor size, chop off the bits that don't fix while retaining the image's aspect ratio or scale the image only if it is smaller than the monitors themselves. When an image is smaller, Kbgswticher will add a black background around the image as necessary.

The choices here for 'scaleimage' are: 0, 1, 2 being scale, chop and fixed image respectively. 


