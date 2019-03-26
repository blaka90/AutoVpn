import os
import wget
import requests
import getpass
import threading
import subprocess
import sys

"""

there twitter tweets when they change the password
	-twitter api or scrape for passwords
		-tweetpy
		
current password: cau778w

"""

user = getpass.getuser()

os.chdir("/home/" + user + "/Documents/python/vpn/")

username = "vpnbook"


def get_profiles():
	url = "https://www.vpnbook.com/free-openvpn-account/VPNBook.com-OpenVPN-PL226.zip"
	wget.download(url)
	os.system("unzip VPNBook*.zip")


def print_ip():
	my_ip = requests.get("http://ipecho.net/plain?")
	if str(my_ip) == "<Response [200]>":
		print("\n")
		print(my_ip.text)
		print("\n")


# this needs to be a thread
def start_vpn():
	# os.system("openvpn --config vpnbook-pl226-tcp443.ovpn")
	p = subprocess.Popen(["sudo", "openvpn", "--config", "vpnbook-pl226-tcp443.ovpn"])
	#  stdin=subprocess.PIPE,
	# 	                     stdout=subprocess.PIPE, stderr=subprocess.PIPE

	out, err = p.communicate(input=username)
	if out:
		print(out.decode())
	if err:
		print(err.decode())


def stop_vpn():
	p_name = "openvpn"
	try:
		os.popen("sudo kill %s" % p_name)
		print('[*]killing pid: ' + str(p_name))
	except Exception as e:
		if "No such process" in e:
			print(str(e))
	print("[*]--All processes killed--\n")


def main():
	if not os.path.isfile("VPNBook.com-OpenVPN-PL226.zip"):
		get_profiles()
	print("\nCurrent ip:")
	print_ip()
	# vpn = threading.Thread(target=start_vpn)
	# vpn.start()
	start_vpn()
	print("\nCurrent ip:")
	print_ip()
	print("\nscript is going to keep running until you type 'y' when finished!")
	ans = input("finished?: ")
	if ans == "y":
		# os.system("rm VPNB*")
		# os.system("rm vpnbook*")
		stop_vpn()
		sys.exit(7)


if __name__ == "__main__":
	main()
