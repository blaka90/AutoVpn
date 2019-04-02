import os
import wget
import requests
import getpass
import threading
import subprocess
import sys
import pexpect

"""

make sure pidof returns proper pid in stop_vpn

there twitter tweets when they change the password
	-twitter api or scrape for passwords
		-tweetpy
		
current password: 533d2ve

"""

user = getpass.getuser()

os.chdir("/home/" + user + "/Documents/python/vpn_er/")

username = "vpnbook"

cur_password = "533d2ve"


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
def start_vpn(passy):
	expect_passy = "[sudo] password for {}:".format(user)
	shell = pexpect.spawn("sudo openvpn --config vpnbook-pl226-tcp443.ovpn")
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
	"""
	# os.system("openvpn --config vpnbook-pl226-tcp443.ovpn")
	p = subprocess.Popen(["sudo", "openvpn", "--config", "vpnbook-pl226-tcp443.ovpn"])
	#  stdin=subprocess.PIPE,
	# 	                     stdout=subprocess.PIPE, stderr=subprocess.PIPE

	out, err = p.communicate(input=username)
	if out:
		print(out.decode())
	if err:
		print(err.decode())
	"""


def stop_vpn(passy):
	p_name = "openvpn"
	p = subprocess.Popen(['pidof', p_name], stdout=subprocess.PIPE, shell=True)
	result = p.communicate()[0].decode()
	print(result)
	shell = pexpect.spawn("sudo kill {}".format(result))
	shell.expect('.*password for .*?: ')
	shell.sendline(passy)
	"""
	try:
		os.popen("sudo kill {}".format(p_name))
		print('[*]killing pid: ' + str(p_name))
	except Exception as e:
		if "No such process" in e:
			print(str(e))
	"""
	print("[*]--All processes killed--\n")


def main():
	if not os.path.isfile("VPNBook.com-OpenVPN-PL226.zip"):
		get_profiles()
	print("\nCurrent ip:")
	print_ip()
	passy = getpass.getpass()
	vpn = threading.Thread(target=start_vpn, args=[passy])
	vpn.start()
	# start_vpn(passy)
	print("\nCurrent ip:")
	print_ip()
	print("\nscript is going to keep running until you type 'y' when finished!")
	ans = input("finished?: ")
	if ans == "y":
		# os.system("rm VPNB*")
		# os.system("rm vpnbook*")
		stop_vpn(passy)
		sys.exit(7)


if __name__ == "__main__":
	main()
