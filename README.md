# AutoVpn

Gui for starting/stopping vpnbooks openvpn servers 

Linux only

Installation:

    sudo apt install openvpn python3-pyqt5

(or you're distros equivalent)

cd into AutoVpn directory and

    pip3 install -r requirements.txt


*DEPENDING ON YOUR SYSTEM SETUP YOU MAY EITHER HAVE TO*

    pip uninstall pyqt5

or

    sudo apt purge python3-pyqt5



**Canada doesn't come with tcp443 for some reason it's not a bug**


*--If you change your login password, delete has_password to be prompted again--*