# mira
Minimalist Internet Radio


Setup: 
(date of creation: February 2024)

1. install Raspberry Pi OS with imager
    [raspberrypi.com](https://www.raspberrypi.com/software/)
2. general Raspi Configuration
    sudo raspi-config
2. install mpd and mpc
    sudo apt install mpd
    sudo apt install mpc
3. determine audio output device
    aplay -l
    hw[0,0] <- card 2, device 0
4. edit config of mpd
    sudo nano /etc/mpd.conf
    - uncomment following
    ->  audio_output {
            type          "alsa"
            name          "My ALSA Device"
            device       "hw:2,0"
        }
5. enable mpd in systemctl
    sudo systemctl enable mpd
    check: sudo systemctl status mpd
6. start or restart mpd in systemctl
    sudo systemctl start mpd
    sudo systemctl restart mpd
7. test mpc and mpd
    mpc clear
    mpc add ... #Radio-URL
    mpc play
8. when test complete, stop playing
    mpc stop
9. 



Autostart
1. create a .sh file (example: ~/launch_mira.sh)
    #!/usr/bin/sh
    sleep 5
    /usr/bin/python ~/Github/mira/mira.py --fullscreen
2. edit ~/.config/wayfire.ini
3. add a section at the end
    [autostart]
    (name) = path of file to be run on startup
4. save and exit
5. reboot



HifiBerry 
1. for available driver modules run
    ls -l /boot/firmware/overlays/hifiberry*
2. edit /boot/firmware/config.txt
3. add to [all]
    dtoverlay=hifiberry-dacplus        (the module that matches your specific HAT model)
4. save and exit
5. Reboot
6. repeat steps from Setup 3, 4 and 6


