
# mira
### Minimalist Internet Radio

(date of creation: February 2024)

This is a project to implement our own internet radio for everyday use. We created a simple GUI with a status line for the currently played song and radio station, a title bar with date, time and the current signal strength and eight buttons with configurable radio stations.

___

![screenshot of mira running on a Raspi 4](/screenshots/GUI.png)

___

The program was built and tested for following hardware and software components:

Software:

- Python version: 3.12.2
- Raspberry Pi OS (based on Debian 12 (Bookworm))

Hardware:
- Raspberry Pi 4 Model B
- Display: Waveshare 4.3inch DSI LCD Capacitive Touch Screen Display 800x480 Resolution IPS Wide Angle Monitor for Raspberry Pi 4B/3B+/3A+/3B/2B/B+/A+ (any touch-sensitive display for Raspberry Pi 4 should work, but some may need further configurations within Raspberry Pi OS)
- HiFiBerry DAC+ (any HiFiBerry should work, but configuration of the Raspberry Pi OS will vary, see [`step-by-step guide/HiFiBerry`](#hifiberry))


If you need help setting up mira on your own Raspberry Pi please refer to the [`step-by-step guide`](#step-by-step-guide) below for detailed instructions.

___

# Step-by-step guide


## Setup:

1. #### Install [Raspberry Pi OS](https://www.raspberrypi.com/software/ "Go to website") with an imager on an SD-Card
   - using the Raspberry Pi OS Lite image (no desktop environment)
   - using `mira` as username


1. #### Install packages

    ```
    sudo apt install mpd
    sudo apt install mpc
    sudo apt instal python3-guizero
    sudo apt install xinit
    ```

1. #### Edit config of X server

    ```
    sudo nano /etc/X11/Xwrapper.config
    ```

    edit the following line to allow any users

    ```
    allowed_users=anybody
    ```



1. #### Determine the audio output device

    ```
    aplay -l
    ```

    search for the card and device number, e.g. card 2, device 0


1. #### Edit config of mpd

    ```
    sudo nano /etc/mpd.conf
    ```
    
    uncomment the following and edit the device according to [`step 4`](#determine-the-audio-output-device)

    ```
    audio_output {  
       type          "alsa"  
       name          "My ALSA Device"  
       device       "hw:2,0"  
    }
    ```

1. #### Enable mpd in systemctl

    ```
    sudo systemctl enable mpd
    ```
    
    check if mpd is enabled

    ```
    sudo systemctl status mpd
    ```

1. #### Start or restart mpd in systemctl

    ```
    sudo systemctl start mpd
    ```

    ```
    sudo systemctl restart mpd
    ```

1.  #### Test mpc and mpd
    
    ```
    mpc clear
    ```
    
    ```
    mpc add [Radio-URL]
    ```
    
    ```
    mpc play
    ```

1.  #### When test complete, stop playing

    ```
    mpc stop
    ```

1. #### Download all mira files and copy them to your directory of choice.





## Autostart without desktop environment

1. #### Review and adapt the paths in mira.service
2. #### Create systemd service
   
    ```
    sudo systemctl enable /home/mira/Github/mira/mira.service
    ```

3. #### Start the service
    
    ```
    sudo systemctl start mira
    ```




## Autostart with Wayland desktop environment

1. #### Create a .sh file (example: ~/launch_mira.sh) with the following content
    
    ```
    #!/usr/bin/sh  
    sleep 5  
    /usr/bin/python ~/Github/mira/mira.py --fullscreen  (the file path depends on where mira was copied to)
    ```

2. #### Edit wayfire file

    ```
    sudo nano ~/.config/wayfire.ini
    ```

    add a section at the end
    
    ```
    [autostart]  
    (name) = path of file to be run on startup
    ```

3. #### Save and exit

4. #### Reboot the Raspberry Pi







## HifiBerry driver setup (if required)

1. #### For available driver modules run

    ```
    ls -l /boot/firmware/overlays/hifiberry*
    ```

2. #### Add the driver module to the firmware config

    ```
    sudo nano /boot/firmware/config.txt
    ```

    and add to section `[all]`:

    ```
    dtoverlay=hifiberry-dacplus
    ```
    (the module that matches your specific HAT model)

3. #### Save and exit

4. #### Reboot the Raspberry Pi

5. #### Repeat steps [`4`](#determine-the-audio-output-device), [`5`](#edit-config-of-mpd) and [`7`](#start-or-restart-mpd-in-systemctl) of Setup



## Optional configuration

### Disable WiFi and Bluetooth
1. #### open the firmware config file

    ```
    sudo nano /boot/firmware/config.txt
    ```

2. #### Find the section
    ```
    # Additional overlays and parameters are documented
    # /boot/firmware/overlays/README
    ```

3. #### Add the following lines
    ```
    dtoverlay=disable-wifi
    dtoverlay=disable-bt
    ```

4. #### Save and exit
5. #### Reboot the Raspberry Pi


### For general Raspi configurations use
```
sudo raspi-config
```



### Adjust output level of Dac+

```
sudo alsamixer
```


### Configure screen off timeout
create the file

```
sudo nano /etc/X11/xorg.conf.d/screensaver.conf
```

add the following content to the file to disable the screen off timeout

```
Section "ServerFlags"
Option "BlankTime"  "0"
EndSection
```


see also `man xorg.conf`


