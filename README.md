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


if it keeps failing it means vpnbook hasn't tweeted their new password yet(the only way i can scrape the password), if this occurs:

- go to www.vpnbook.com, under OpenVPN tab find password at bottom

- go to autovpn/manual_pasword.txt and manual type password and save

AutoVpn will always try scrape for password first but if that fails then fallback to manual_pasword.txt
