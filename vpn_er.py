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
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtTest import QTest

"""
label to show ip
button to refresh ip

rename to AutoVpn

need to start vpn as thread still

waiting for twitter api token, to implement grabbing password

there twitter tweets when they change the password
	-twitter api or scrape for passwords
		-tweetpy
		
current password: 533d2ve

"""


class Window(QWidget):
	def __init__(self):
		super(Window, self).__init__()
		self.vpn_pl = "VPNBook.com-OpenVPN-PL226.zip"
		self.vpn_de = "VPNBook.com-OpenVPN-DE4.zip"
		self.start_style()
		self.path()
		self.get_profiles()
		self.user = getpass.getuser()
		self.vpn_auth_name = "vpnbook"
		self.vpn_auth_password = "533d2ve"
		self.password = self.get_password()
		self.init_ui()

	# initilize the user interface
	def init_ui(self):
		"""all below code is (roughly) in decending visual order"""

		# set the name, icon and size of main window
		self.setWindowTitle("AutoVpn")
		# self.setWindowIcon(QIcon("resources/syncer.png"))
		self.setGeometry(150, 100, 200, 200)
		# self.setStyleSheet("background-color: black")

		self.vpn_on = QPushButton("ON")
		self.vpn_on.setCheckable(True)
		self.vpn_on.setStyleSheet('background-color: green; color: black')
		self.vpn_on.setFixedWidth(100)
		self.vpn_on.clicked.connect(self.start_vpn)

		self.vpn_off = QPushButton("OFF")
		self.vpn_off.setCheckable(True)
		self.vpn_off.setStyleSheet('background-color: darkred; color: black')
		self.vpn_off.setFixedWidth(100)
		self.vpn_off.clicked.connect(self.stop_vpn)

		h_box = QHBoxLayout()
		h_box.addWidget(self.vpn_on)
		h_box.addWidget(self.vpn_off)

		self.setLayout(h_box)

	@staticmethod
	def start_style():
		# sets the window to dark mode with the fusion styling
		# from PyQt5.QtGui import * and from PyQt5.QtCore import * are needed mostly just for this to run correctly
		qApp.setStyle("Fusion")
		dark_palette = QPalette()
		dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
		dark_palette.setColor(QPalette.WindowText, Qt.white)
		dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
		dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
		dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
		dark_palette.setColor(QPalette.ToolTipText, Qt.white)
		dark_palette.setColor(QPalette.Text, Qt.white)
		dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
		dark_palette.setColor(QPalette.ButtonText, Qt.white)
		dark_palette.setColor(QPalette.BrightText, Qt.red)
		dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
		dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
		dark_palette.setColor(QPalette.HighlightedText, Qt.black)
		qApp.setPalette(dark_palette)
		qApp.setStyleSheet("QToolTip { color: #ffffff; background-color: "
		                   "#2a82da; border: 1px solid white; }")

	@staticmethod
	def path():
		abspath = os.path.abspath(__file__)
		dir_name = os.path.dirname(abspath)
		os.chdir(dir_name)

	def get_password(self):
		ask_pass, ok_pressed = QInputDialog.getText(self, "VPN Authorization", "Sudo Password: ",
		                                            QLineEdit.Password, "")
		if ok_pressed:
			self.password = ask_pass
			return self.password
		else:
			sys.exit(10)

	def get_profiles(self):
		if not os.path.isfile(self.vpn_pl):
			url_pl = "https://www.vpnbook.com/free-openvpn-account/" + self.vpn_pl
			wget.download(url_pl)
		if not os.path.isfile(self.vpn_de):
			url_de = "https://www.vpnbook.com/free-openvpn-account/" + self.vpn_de
			wget.download(url_de)
		sleep(1)
		if os.path.isfile(self.vpn_pl) and not os.path.isfile("vpnbook-pl226-udp25000.ovpn"):
			self.unzipper(self.vpn_pl)
		if os.path.isfile(self.vpn_pl) and not os.path.isfile("vpnbook-de4-udp25000.ovpn"):
			self.unzipper(self.vpn_de)

	@staticmethod
	def unzipper(fn):
		zfile = zipfile.ZipFile(fn, 'r')
		zfile.extractall()
		zfile.close()

	@staticmethod
	def print_ip():
		my_ip = requests.get("http://ipecho.net/plain?")
		if str(my_ip) == "<Response [200]>":
			print("\nCurrent ip:\n")
			print(my_ip.text)
			print("\n")

	# this needs to be a thread
	def start_vpn(self):
		shell = pexpect.spawn("sudo openvpn --config vpnbook-de4-udp25000.ovpn")
		# shell = pexpect.spawn("sudo openvpn --config vpnbook-pl226-tcp443.ovpn")
		shell.expect('.*password for .*?: ')
		shell.sendline(self.password)
		shell.expect("Enter Auth Username:")
		shell.sendline(self.vpn_auth_name)
		shell.expect("Enter Auth Password:")
		shell.sendline(self.vpn_auth_password)
		shell.expect(pexpect.EOF, timeout=None)
		cmd_show_data = shell.before
		cmd_output = cmd_show_data.split(b'\r\n')
		for data in cmd_output:
			print(data.decode())

	def stop_vpn(self):
		p_name = "openvpn"
		p = subprocess.Popen(['pidof', p_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		out, err = p.communicate()
		shell = pexpect.spawn("sudo kill {}".format(out.decode()))
		shell.expect('.*password for .*?: ')
		shell.sendline(self.password)
		shell.expect(pexpect.EOF, timeout=None)
		cmd_show_data = shell.before
		cmd_output = cmd_show_data.split(b'\r\n')
		for data in cmd_output:
			print(data.decode())
		print("\n[*]--VPN Process Killed--\n")
		sys.exit(7)

"""
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
		"""


def main():
	# create the application
	app = QApplication(sys.argv)
	# inintilze the window object
	window = Window()
	# show the window
	window.show()
	sys.exit(app.exec_())


if __name__ == "__main__":
	main()
