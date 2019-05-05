import os
import wget
import requests
import subprocess
import sys
import pexpect
import zipfile
import keyring
from getpass import getuser
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtTest import QTest
from twitter_scraper import get_tweets


class Window(QWidget):
    def __init__(self):
        super(Window, self).__init__()
        self.vpn_pl = "VPNBook.com-OpenVPN-PL226.zip"
        self.vpn_de = "VPNBook.com-OpenVPN-DE4.zip"
        self.vpn_us1 = "VPNBook.com-OpenVPN-US1.zip"
        self.vpn_us2 = "VPNBook.com-OpenVPN-US2.zip"
        self.vpn_ca = "VPNBook.com-OpenVPN-CA222.zip"
        self.vpn_fr = "VPNBook.com-OpenVPN-FR1.zip"
        self.vpn_list = [self.vpn_pl, self.vpn_de, self.vpn_us1, self.vpn_us2, self.vpn_ca, self.vpn_fr]
        self.gen_list = ["vpnbook-pl226-", "vpnbook-de4-", "vpnbook-us1-", "vpnbook-us2-", "vpnbook-ca222-", "vpnbook-fr1-"]
        self.vpn_gen_list = ["tcp80.ovpn", "tcp443.ovpn", "udp53.ovpn", "udp25000.ovpn"]
        self.service_name = "AutoVpn"
        self.start_style()
        self.path()
        self.vpn_auth_name = "vpnbook"
        self.vpn_auth_password = self.grab_password()
        self.user = getuser()
        self.password = self.get_password()
        self.get_profiles()
        self.check_running()
        self.init_ui()
        self.start_ip = ""
        self.alt_print = 0
        self.print_ip()
        self.chosen_vpn = ""
        self.thread = QThreadPool()
        self.file_picked = False
        self.no_go = False
        self.vpn_state = False

    # initilize the user interface
    def init_ui(self):
        # set the name, icon and size of main window
        self.setWindowTitle("AutoVpn")
        # self.setWindowIcon(QIcon(".png"))
        self.setGeometry(0, 0, 200, 100)

        self.ip_label = QLabel(self)

        self.refresh_ip = QPushButton("refresh")
        self.refresh_ip.clicked.connect(self.print_ip)
        self.refresh_ip.setFixedWidth(200)

        self.file_brow = QPushButton("Choose")
        self.file_brow.clicked.connect(self.chooser)
        self.file_brow.setFixedWidth(100)

        self.pl = QRadioButton("Poland")
        self.de = QRadioButton("Germany")
        self.us1 = QRadioButton("USA1")
        self.us2 = QRadioButton("USA2")
        self.ca = QRadioButton("Canada")
        self.fr = QRadioButton("France")

        self.country_group = QButtonGroup()
        self.country_group.addButton(self.pl)
        self.country_group.addButton(self.de)
        self.country_group.addButton(self.us1)
        self.country_group.addButton(self.us2)
        self.country_group.addButton(self.ca)
        self.country_group.addButton(self.fr)

        self.tcp80 = QRadioButton("tcp80")
        self.tcp443 = QRadioButton("tcp443")
        self.udp53 = QRadioButton("udp53")
        self.udp25000 = QRadioButton("udp25000")

        self.conn_types = QButtonGroup(self)
        self.conn_types.addButton(self.tcp80)
        self.conn_types.addButton(self.tcp443)
        self.conn_types.addButton(self.udp53)
        self.conn_types.addButton(self.udp25000)

        self.vpn_button = QPushButton("VPN: OFF")
        self.vpn_button.setStyleSheet('color: black')
        self.vpn_button.setFixedHeight(40)
        self.vpn_button.setFixedWidth(200)
        self.vpn_button.clicked.connect(self.start_vpn)

        h_box = QHBoxLayout()
        h_box.addWidget(self.vpn_button)

        p2p_box = QHBoxLayout()
        p2p_box.addWidget(self.pl)
        p2p_box.addWidget(self.de)

        p2p = QGroupBox("P2P:")
        p2p.setLayout(p2p_box)

        no_p2p_box = QHBoxLayout()
        no_p2p_box.addWidget(self.us1)
        no_p2p_box.addWidget(self.us2)
        no_p2p_box.addWidget(self.ca)
        no_p2p_box.addWidget(self.fr)

        no_p2p = QGroupBox("No P2P/ Web Surfing Only:")
        no_p2p.setLayout(no_p2p_box)

        h_radio = QHBoxLayout()
        h_radio.addWidget(p2p)
        h_radio.addWidget(no_p2p)

        h_buttons = QHBoxLayout()
        h_buttons.addWidget(self.refresh_ip)
        h_buttons.addWidget(self.file_brow)

        h_radio_types = QHBoxLayout()
        h_radio_types.addWidget(self.tcp80)
        h_radio_types.addWidget(self.tcp443)
        h_radio_types.addWidget(self.udp53)
        h_radio_types.addWidget(self.udp25000)

        country_box = QGroupBox("Select Country:")
        country_box.setLayout(h_radio)

        connection_box = QGroupBox("Select Connection Type:")
        connection_box.setLayout(h_radio_types)

        v_box = QVBoxLayout()
        v_box.addWidget(self.ip_label)
        v_box.addLayout(h_buttons)
        v_box.addWidget(country_box)
        v_box.addWidget(connection_box)
        v_box.addLayout(h_box)

        self.setLayout(v_box)

    def grab_password(self):
        for tweet in get_tweets('vpnbook', pages=1):
            if tweet['text'].startswith("VPN password updated"):
                self.vpn_auth_password = tweet['text'][-7:]
                break

        print(self.vpn_auth_password)
        return self.vpn_auth_password

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

    def path(self):
        abspath = os.path.abspath(__file__)
        self.dir_name = os.path.dirname(abspath)
        os.chdir(self.dir_name)

        path = self.dir_name + "/manual_password.txt"
        if not os.path.exists(path):
            with open(path, "w") as f:
                f.close()

    def try_manual_password(self):
        with open(self.dir_name + "/manual_password.txt", "r") as f:
            passy = f.read()
            f.close()
        print(passy)
        self.vpn_auth_password = passy
        return

    def get_password(self):
        if os.path.isfile("has_password"):
            return keyring.get_password(self.service_name, self.user)
        else:
            ask_pass, ok_pressed = QInputDialog.getText(self, "VPN Authorization", "Computer Password: ", QLineEdit.Password, "")
            if ok_pressed:
                keyring.set_password(self.service_name, self.user, ask_pass)
                open('has_password', 'a').close()
                return ask_pass

    def get_profiles(self):
        if not os.path.exists(self.dir_name + "/profiles/"):
            os.mkdir(self.dir_name + "/profiles/")
        for pro in self.vpn_list:
            if not os.path.isfile(self.dir_name + "/profiles/" + pro):
                url_pl = "https://www.vpnbook.com/free-openvpn-account/" + pro
                wget.download(url_pl, self.dir_name + "/profiles/")
        # QTest.qWait(2000)
        for vn, vz in zip(self.gen_list, self.vpn_list):
            for vt in self.vpn_gen_list:
                if not os.path.isfile(self.dir_name + "/profiles/" + vn + vt):
                    self.unzipper(self.dir_name + "/profiles/" + vz)
                    break
                else:
                    continue

    def chooser(self):
        self.brow = MyFileBrowser()
        self.brow.sig.return_data.connect(self.return_file_path)

    def return_file_path(self, fp):
        self.file_picked = True
        self.chosen_vpn = fp

    def get_vpn_options(self):
        pro_list = [self.pl, self.de, self.us1, self.us2, self.ca, self.fr]
        conn_list = [self.tcp80, self.tcp443, self.udp53, self.udp25000]
        country_num = 0
        for country in pro_list:
            connection_num = 0
            if country.isChecked():
                self.no_go = False
                for con in conn_list:
                    if con.isChecked():
                        self.no_go = False
                        if (country == pro_list[4]) and (con == conn_list[1]):
                            self.chosen_vpn = self.gen_list[country_num] + self.vpn_gen_list[connection_num - 1]
                        else:
                            self.chosen_vpn = self.gen_list[country_num] + self.vpn_gen_list[connection_num]
                        return

                    connection_num += 1
                    self.no_go = True

            country_num += 1
            self.no_go = True

    def unzipper(self, fn):
        zfile = zipfile.ZipFile(fn, 'r')
        zfile.extractall(path=self.dir_name+"/profiles/")
        zfile.close()

    def check_running(self):
        p_name = "openvpn"
        p = subprocess.Popen(['pidof', p_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        print(out.decode())
        if not out:
            self.vpn_state = False
            # return False
        else:
            self.no_thread_exit()

    def print_ip(self):
        if self.alt_print == 0:
            my_ip = requests.get("https://api.ipify.org")
            self.alt_print = 1
        else:
            my_ip = requests.get("http://ipecho.net/plain?")
            self.alt_print = 0

        if str(my_ip) == "<Response [200]>":
            self.ip_label.setText("Current IP:        " + my_ip.text)
            print("\nCurrent ip:\n")
            print(my_ip.text)
            print("\n")
        else:
            print("Failed to get ip address")
            return self.print_ip()
        self.current_ip = my_ip.text
        if not self.start_ip:
            self.start_ip = my_ip.text

    # this needs to be a thread
    def start_vpn(self):
        if not self.vpn_state:
            if not self.file_picked:
                self.get_vpn_options()
            if self.no_go:
                return
            self.vpn_button.setText("VPN: Starting...")
            self.vpn_button.setStyleSheet('background-color: blue; color: black')
            command = "sudo openvpn --config " + self.dir_name + "/profiles/" + self.chosen_vpn
            startv = StartVpn(command, self.password, self.vpn_auth_name, self.vpn_auth_password)
            startv.signals.printer.connect(self.print_ip)
            self.thread.start(startv)
            self.vpn_state = True
            if self.start_check_change(0):
                self.vpn_button.setText("VPN: ON")
                self.vpn_button.setStyleSheet('background-color: green; color: black')
        else:
            self.file_picked = False
            self.vpn_button.setText("VPN: Stopping...")
            self.vpn_button.setStyleSheet('background-color: blue; color: black')
            stopv = StopVpn(self.password)
            stopv.signals.printer.connect(self.print_ip)
            self.thread.start(stopv)
            self.vpn_state = False
            if self.stop_check_change():
                self.vpn_button.setText("VPN: OFF")
                self.vpn_button.setStyleSheet('background-color: darkred; color: black')

    def stop_check_change(self):
        if self.start_ip != self.current_ip:
            QTest.qWait(1000)
            self.print_ip()
            return self.stop_check_change()
        else:
            return True

    def start_check_change(self, counter):
        counter += 1
        if counter == 5:
            self.vpn_button.setText("VPN: Failed")
            self.vpn_button.setStyleSheet('background-color: red; color: black')
            QTest.qWait(3000)
            self.vpn_button.setText("VPN: Trying Manual")
            self.vpn_button.setStyleSheet('background-color: blue; color: black')
            QTest.qWait(2000)
            self.try_manual_password()
            command = "sudo openvpn --config " + self.dir_name + "/profiles/" + self.chosen_vpn
            startv = StartVpn(command, self.password, self.vpn_auth_name, self.vpn_auth_password)
            startv.signals.printer.connect(self.print_ip)
            self.thread.start(startv)
            self.vpn_state = True
            if self.start_check_change(0):
                self.vpn_button.setText("VPN: ON")
                self.vpn_button.setStyleSheet('background-color: green; color: black')
        if self.start_ip == self.current_ip:
            QTest.qWait(2000)
            self.print_ip()
            return self.start_check_change(counter)
        else:
            return True

    def no_thread_exit(self):
        p_name = "openvpn"
        p = subprocess.Popen(['pidof', p_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        print(out.decode())
        if not out:
            sys.exit(200)
        else:
            shell = pexpect.spawn("sudo kill {}".format(out.decode()))
            shell.expect('.*password for .*?: ')
            shell.sendline(self.password)
            shell.expect(pexpect.EOF, timeout=None)
            cmd_show_data = shell.before
            cmd_output = cmd_show_data.split(b'\r\n')
            for data in cmd_output:
                print(data.decode())
            sys.exit(10)

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Closing VPN', "Are you sure you want to quit?", QMessageBox.Yes |
                                     QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.no_thread_exit()
            event.accept()
            sys.exit(0)
        else:
            event.ignore()


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
        print("\n[*]--VPN Process Killed: {} --\n".format(out.decode()))


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
        # QTest.qWait(10000)
        # self.signals.printer.emit()
        shell.expect(pexpect.EOF, timeout=None)
        cmd_show_data = shell.before
        cmd_output = cmd_show_data.split(b'\r\n')
        for data in cmd_output:
            print(data.decode())


class BrowserSignal(QObject):
    return_data = pyqtSignal(str)


# class for opening/showing a file browser to choose path instead of typing it manually
class MyFileBrowser(QWidget):

    def __init__(self):
        QWidget.__init__(self)
        self.view = QTreeView()  # for displaying the FileSystemModel in a TreeView
        self.sig = BrowserSignal()  # signal for passing data back to main window
        self.setWindowTitle("Choose vpn profile")
        self.path = "/"
        self.file_path = ""
        self.model = QFileSystemModel()  # the file file system model creation
        self.model.setRootPath(QDir.rootPath())  # we want to start from root
        self.setGeometry(320, 200, 1000, 600)
        self.view.setModel(self.model)  # puts the file system model into the tree view
        self.view.setRootIndex(self.model.index(self.path))  # set the indexes
        self.view.setSortingEnabled(True)  # give the option to sort on header click
        self.view.setColumnWidth(0, 610)
        self.view.sortByColumn(0, Qt.AscendingOrder)
        self.open_button = QPushButton("Open", self)  # pushed when file path is chosen and sends signal
        self.open_button.clicked.connect(self.return_path)
        self.open_button.setFixedWidth(200)
        self.open_button.setStyleSheet("background-color: darkgray; color: black")

        self.v_box = QVBoxLayout()
        self.v_box.addWidget(self.view)
        self.v_box.addWidget(self.open_button, alignment=Qt.AlignCenter)
        self.setLayout(self.v_box)
        self.show()

    # when filepath is chosen and open button is pressed return path to correlating input box in main window and close
    def return_path(self):
        fp = self.view.selectedIndexes()[0]
        self.file_path = self.model.filePath(fp)
        self.sig.return_data.emit(self.file_path)
        self.close()


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
