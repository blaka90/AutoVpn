import os
import wget
import requests
import getpass
import threading
import subprocess
import sys
import pexpect
import zipfile
from time import sleep

"""
waiting for twitter api token, to implement grabbing password

there twitter tweets when they change the password
	-twitter api or scrape for passwords
		-tweetpy
		
current password: 533d2ve

"""

user = getpass.getuser()

username = "vpnbook"

cur_password = "533d2ve"

vpn_pl = "VPNBook.com-OpenVPN-PL226.zip"
vpn_de = "VPNBook.com-OpenVPN-DE4.zip"


def path():
	abspath = os.path.abspath(__file__)
	dir_name = os.path.dirname(abspath)
	os.chdir(dir_name)


def get_profiles():
	if not os.path.isfile(vpn_pl):
		url_pl = "https://www.vpnbook.com/free-openvpn-account/" + vpn_pl
		wget.download(url_pl)
	if not os.path.isfile(vpn_de):
		url_de = "https://www.vpnbook.com/free-openvpn-account/" + vpn_de
		wget.download(url_de)
	sleep(1)
	if os.path.isfile(vpn_pl) and not os.path.isfile("vpnbook-pl226-udp25000.ovpn"):
		unzipper(vpn_pl)
	if os.path.isfile(vpn_pl) and not os.path.isfile("vpnbook-de4-udp25000.ovpn"):
		unzipper(vpn_de)


def unzipper(fn):
	zfile = zipfile.ZipFile(fn, 'r')
	zfile.extractall()
	zfile.close()


def print_ip():
	my_ip = requests.get("http://ipecho.net/plain?")
	if str(my_ip) == "<Response [200]>":
		print("\n")
		print(my_ip.text)
		print("\n")


# this needs to be a thread
def start_vpn(passy):
	shell = pexpect.spawn("sudo openvpn --config vpnbook-de4-udp25000.ovpn")
	# shell = pexpect.spawn("sudo openvpn --config vpnbook-pl226-tcp443.ovpn")
	shell.expect('.*password for .*?: ')
	shell.sendline(passy)
	shell.expect("Enter Auth Username:")
	shell.sendline(username)
	shell.expect("Enter Auth Password:")
	shell.sendline(cur_password)
	shell.expect(pexpect.EOF, timeout=None)
	cmd_show_data = shell.before
	cmd_output = cmd_show_data.split(b'\r\n')
	for data in cmd_output:
		print(data.decode())


def stop_vpn(passy):
	p_name = "openvpn"
	p = subprocess.Popen(['pidof', p_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	out, err = p.communicate()
	shell = pexpect.spawn("sudo kill {}".format(out.decode()))
	shell.expect('.*password for .*?: ')
	shell.sendline(passy)
	shell.expect(pexpect.EOF, timeout=None)
	cmd_show_data = shell.before
	cmd_output = cmd_show_data.split(b'\r\n')
	for data in cmd_output:
		print(data.decode())
	print("\n[*]--VPN Process Killed--\n")
	sys.exit(7)


def main():
	path()
	get_profiles()
	print("\nCurrent ip:")
	print_ip()
	passy = getpass.getpass()
	vpn = threading.Thread(target=start_vpn, args=[passy])
	vpn.start()
	print(vpn.ident)  # thread identifier, may come in handy later
	# start_vpn(passy)
	print("\nCurrent ip:")
	print_ip()
	print("\nscript is going to keep running until you type 'y' when finished!")
	ans = input("finished?: ")
	if ans == "y":
		stop_vpn(passy)


if __name__ == "__main__":
	main()
