(date of creation: February 2024)


# Setup:

1. #### install [Raspberry Pi OS](https://www.raspberrypi.com/software/ "Go to website") with an imager on an SD-Card

2. #### for general Raspi configurations use

    `sudo raspi-config`

3. #### install mpd and mpc

    `sudo apt install mpd`

    `sudo apt install mpc`

4. #### determine the audio output device

    `aplay -l`

    > hw[2,0] <- card 2, device 0

5. #### edit config of mpd

    `sudo nano /etc/mpd.conf`
    
    uncomment the following and edit the device according to [`step 4`](#determine-the-audio-output-device)
    
    >audio_output {  
    >   type          "alsa"  
    >   name          "My ALSA Device"  
    >   device       "hw:2,0"  
    >}

6. #### enable mpd in systemctl

    `sudo systemctl enable mpd`
    
    check if mpd is enabled

    `sudo systemctl status mpd`

7. #### start or restart mpd in systemctl

    `sudo systemctl start mpd`

    `sudo systemctl restart mpd`

8. #### test mpc and mpd
    
    `mpc clear`
    
    `mpc add [Radio-URL]`
    
    `mpc play`

9. ### when test complete, stop playing

    `mpc stop`

10. #### download all mira files and copy them to your directory of choice

11. #### the Raspberry Pi is now set up and should be ready to use



# Autostart

1. #### create a .sh file (example: ~/launch_mira.sh) with following content:
    
    > #!/usr/bin/sh  
    > sleep 5  
    > /usr/bin/python ~/Github/mira/mira.py --fullscreen  (the file path depends on where mira was copied to)

2. #### edit wayfire:

    `sudo nano ~/.config/wayfire.ini`

    add a section at the end:
    
    > [autostart]  
    > (name) = path of file to be run on startup

3. #### save and exit

4. #### reboot the Raspberry Pi





# HifiBerry 

1. #### for available driver modules run
    `ls -l /boot/firmware/overlays/hifiberry*`

2. #### edit 

    `sudo nano /boot/firmware/config.txt`
    
    and add to section `[all]`:

    `dtoverlay=hifiberry-dacplus`        (the module that matches your specific HAT model)

4. #### save and exit

5. #### reboot the Raspberry Pi

6. #### repeat steps from Setup [`4`](#determine-the-audio-output-device), [`5`](#edit-config-of-mpd) and [`7`](#start-or-restart-mpd-in-systemctl)

