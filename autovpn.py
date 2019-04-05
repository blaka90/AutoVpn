import os
import wget
import requests
import subprocess
import sys
import pexpect
import zipfile
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtTest import QTest

"""
sometimes hangs don't know why???
	(might be the requeust for ip in print_ip?)
	-removed some calls to print_ip hopefullys lessens the load

create file for to save vpn password to and just edit that when needed 

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
		self.vpn_pl_list = ["vpnbook-pl226-tcp80.ovpn", "vpnbook-pl226-tcp443.ovpn", "vpnbook-pl226-udp53.ovpn",
		                    "vpnbook-pl226-udp25000.ovpn"]
		self.vpn_de_list = ["vpnbook-de4-tcp80.ovpn", "vpnbook-de4-tcp443.ovpn", "vpnbook-de4-udp53.ovpn",
		           "vpnbook-de4-udp25000.ovpn"]
		self.start_style()
		self.path()
		self.vpn_auth_name = "vpnbook"
		self.vpn_auth_password = "533d2ve"
		self.password = self.get_password()
		self.get_profiles()
		self.init_ui()
		self.print_ip()
		self.type_vpn = ""
		self.thread = QThreadPool()

	# initilize the user interface
	def init_ui(self):
		# set the name, icon and size of main window
		self.setWindowTitle("AutoVpn")
		# self.setWindowIcon(QIcon("resources/syncer.png"))
		self.setGeometry(150, 100, 200, 100)
		# self.setStyleSheet("background-color: black")

		self.ip_label = QLabel(self)

		self.refresh_ip = QPushButton("refresh")
		self.refresh_ip.clicked.connect(self.print_ip)

		self.pl = QRadioButton("Poland")
		self.pl.setChecked(True)
		self.de = QRadioButton("Germany")

		self.tcp80 = QRadioButton("tcp80")
		self.tcp80.setChecked(True)
		self.tcp443 = QRadioButton("tcp443")
		self.udp53 = QRadioButton("udp53")
		self.udp25000 = QRadioButton("udp25000")

		self.conn_types = QButtonGroup(self)
		self.conn_types.addButton(self.tcp80)
		self.conn_types.addButton(self.tcp443)
		self.conn_types.addButton(self.udp53)
		self.conn_types.addButton(self.udp25000)

		self.vpn_on = QPushButton("ON")
		self.vpn_on.setCheckable(True)
		self.vpn_on.setStyleSheet('color: black')
		self.vpn_on.setFixedWidth(100)
		self.vpn_on.clicked.connect(self.start_vpn)

		self.vpn_off = QPushButton("OFF")
		self.vpn_off.setCheckable(True)
		self.vpn_off.setStyleSheet('color: black')
		self.vpn_off.setFixedWidth(100)
		self.vpn_off.clicked.connect(self.stop_vpn)

		h_box = QHBoxLayout()
		h_box.addWidget(self.vpn_on)
		h_box.addWidget(self.vpn_off)

		h_radio = QHBoxLayout()
		h_radio.addWidget(self.pl)
		h_radio.addWidget(self.de)

		h_radio_types = QHBoxLayout()
		h_radio_types.addWidget(self.tcp80)
		h_radio_types.addWidget(self.tcp443)
		h_radio_types.addWidget(self.udp53)
		h_radio_types.addWidget(self.udp25000)

		v_box = QVBoxLayout()
		v_box.addWidget(self.ip_label)
		v_box.addWidget(self.refresh_ip)
		v_box.addLayout(h_radio)
		v_box.addLayout(h_radio_types)
		v_box.addLayout(h_box)

		self.setLayout(v_box)

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
		qApp.setStyleSheet("QToolTip { color: #ffffff; background-color: #2a82da; border: 1px solid white; }")

	@staticmethod
	def path():
		abspath = os.path.abspath(__file__)
		dir_name = os.path.dirname(abspath)
		os.chdir(dir_name)

	def get_password(self):
		ask_pass, ok_pressed = QInputDialog.getText(self, "VPN Authorization", "Sudo Password: ", QLineEdit.Password, "")
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
		QTest.qWait(2000)
		for p in self.vpn_pl_list:
			if not os.path.isfile(p):
				self.unzipper(self.vpn_pl)
				break
			else:
				continue
		for d in self.vpn_de_list:
			if not os.path.isfile(d):
				self.unzipper(self.vpn_de)
				break
			else:
				continue

	def get_vpn_options(self):
		if self.pl.isChecked():
			if self.tcp80.isChecked():
				self.type_vpn = self.vpn_pl_list[0]
			elif self.tcp443.isChecked():
				self.type_vpn = self.vpn_pl_list[1]
			elif self.udp53.isChecked():
				self.type_vpn = self.vpn_pl_list[2]
			elif self.udp25000.isChecked():
				self.type_vpn = self.vpn_pl_list[3]
		elif self.de.isChecked():
			if self.tcp80.isChecked():
				self.type_vpn = self.vpn_de_list[0]
			elif self.tcp443.isChecked():
				self.type_vpn = self.vpn_de_list[1]
			elif self.udp53.isChecked():
				self.type_vpn = self.vpn_de_list[2]
			elif self.udp25000.isChecked():
				self.type_vpn = self.vpn_de_list[3]

	@staticmethod
	def unzipper(fn):
		zfile = zipfile.ZipFile(fn, 'r')
		zfile.extractall()
		zfile.close()

	def print_ip(self):
		my_ip = requests.get("http://ipecho.net/plain?")
		if str(my_ip) == "<Response [200]>":
			self.ip_label.setText("Current IP:        " + my_ip.text)
			print("\nCurrent ip:\n")
			print(my_ip.text)
			print("\n")

	# this needs to be a thread
	def start_vpn(self):
		self.vpn_on.setStyleSheet('background-color: green; color: black')
		self.vpn_off.setStyleSheet('background-color: darkred; color: black')
		self.get_vpn_options()
		command = "sudo openvpn --config " + self.type_vpn
		startv = StartVpn(command, self.password, self.vpn_auth_name, self.vpn_auth_password)
		startv.signals.printer.connect(self.print_ip)
		self.thread.start(startv)

	def stop_vpn(self):
		self.vpn_off.setStyleSheet('background-color: green; color: black')
		self.vpn_on.setStyleSheet('background-color: darkred; color: black')
		stopv = StopVpn(self.password)
		stopv.signals.printer.connect(self.print_ip)
		self.thread.start(stopv)


class WorkerSignals(QObject):
	printer = pyqtSignal()


class StopVpn(QRunnable):

	def __init__(self, passy):
		QRunnable.__init__(self)
		self.password = passy
		self.signals = WorkerSignals()

	def run(self):
		p_name = "openvpn"
		p = subprocess.Popen(['pidof', p_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		out, err = p.communicate()
		print(out.decode())
		shell = pexpect.spawn("sudo kill {}".format(out.decode()))
		shell.expect('.*password for .*?: ')
		shell.sendline(self.password)
		QTest.qWait(3000)
		self.signals.printer.emit()
		shell.expect(pexpect.EOF, timeout=None)
		cmd_show_data = shell.before
		cmd_output = cmd_show_data.split(b'\r\n')
		for data in cmd_output:
			print(data.decode())
		print("\n[*]--VPN Process Killed--\n")


class StartVpn(QRunnable):

	def __init__(self, command, password, vpn_name, vpn_password):
		QRunnable.__init__(self)
		self.command = command
		self.password = password
		self.vpn_auth_name = vpn_name
		self.vpn_auth_password = vpn_password
		self.signals = WorkerSignals()

	def run(self):
		shell = pexpect.spawn(self.command)
		shell.expect('.*password for .*?: ')
		shell.sendline(self.password)
		shell.expect("Enter Auth Username:")
		shell.sendline(self.vpn_auth_name)
		shell.expect("Enter Auth Password:")
		shell.sendline(self.vpn_auth_password)
		QTest.qWait(10000)
		self.signals.printer.emit()
		shell.expect(pexpect.EOF, timeout=None)
		cmd_show_data = shell.before
		cmd_output = cmd_show_data.split(b'\r\n')
		for data in cmd_output:
			print(data.decode())


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
