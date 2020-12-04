# -*- coding: utf-8 -*-

"""Overview:
    telnet/ssh client with automatic log saving function by Python3.

Usage:
    pyTelnet.py <host> [--port <port_num>] [--log_dir <logdir_path>] [--disable_log] [-h|--help]

Options:
    host                         : Destination hostname or IP address.
    -p, --port <port_num>        : Destination Port Number. (default ... 23))
    -l, --log_dir <logdir_path>  : Specify the log output destination directory.(default="./log/")
    -d, --disable_log            : Do not output log file.
    -h, --help                   : Show this help message and exit.
"""

import blessed
import datetime
import docopt
import getpass
import os
import paramiko
import re
import sys
import telnetlib
import time

class ConnectionInformation:
    def __init__(self, host, port, username, password, timeout):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.timeout = timeout

def main():
    args = docopt.docopt(__doc__)
#   print(args)

    if args["<host>"]:
        dest_host = args["<host>"]

    dest_port = 23
    if args["--port"]:
        dest_port = args["--port"]

    logdir_path = "./log/"
    if args["--log_dir"]:
        logdir_path = args["--log_dir"].replace("\\", "/")

    disable_log_output = False
    if args["--disable_log"]:
        disable_log_output = True

    # Read connection information.
    cn = ConnectionInformation(dest_host, dest_port, "", "", timeout=2)

    """
    # print for Debug.
    print(cn)
    print(logdir_path)
    print(disable_log_output)
    exit(0)
    """

    # Execute command list.
    if cn.port == "22":
        # SSH
        client_ssh(cn, disable_log_output, logdir_path)
    else:
        # TELNET
        client_telnet(cn, disable_log_output, logdir_path)

    return cn

def print_and_append(buffer, outputString):
    """
    print and append to list output string.
    """
    print(outputString, end="")
    if buffer is not None:
        buffer.append(outputString)

def decode(current_output):
    """
    bytes to str
    """
    encodings = ["sjis", "utf8", "ascii"]
    decoded_current_output = ""
    for enc in encodings:
        try:
            decoded_current_output = current_output.decode(enc)
            break
        except:
            continue
    return decoded_current_output

def set_output_filename(cn: ConnectionInformation, logdir_path: str) -> str:
    """
    set log output filename.
    """
    dtStr = datetime.datetime.now().strftime('_%Y%m%d_%H%M%S')

    if not os.path.exists(logdir_path):
        os.makedirs(logdir_path)

    if logdir_path[-1] != "/":
        logdir_path += "/"
    output_filename = logdir_path + remove_prohibited_characters(cn.host) + dtStr + ".log"

    return output_filename

def remove_prohibited_characters(target_str:str) -> str:
    """
    Remove prohibited characters.
    """
    prohibited_chars = ["[", "]", "<", ">", "#", "%", "$", ":", ";", "~", "\r", " ", "\n"]
    result_str = target_str
    for ch in prohibited_chars:
        result_str = result_str.replace(ch, "")

    if "\x1b" in result_str:
        # for powerline.
        result_str = re.sub("\x1b.*h", "", result_str)
        result_str = re.sub("\x1b.*m", "", result_str)

    return result_str

def telnet_read_eager(tn: ConnectionInformation, wf: object, current_output_log: [str], enable_removeLF: bool) -> str:
    """
    Dealing with unread material.
    """
    if tn.eof:
        return False

    try:
#       current_output = tn.read_very_lazy()    # Not recommended because it will be blocked.
        current_output = tn.read_eager()
    except:
        return False

    decoded_current_output = decode(current_output)
    if len(current_output) > 0:
        if enable_removeLF:
            print_and_write(decoded_current_output, wf, string_remove = "\n")
        else:
            print_and_write(decoded_current_output, wf, string_remove = "")
    return decoded_current_output

def print_and_write(outputString: str, wf: object, string_remove = ""):
    """
    Write to stdout and file.
    """
    print(outputString, end="")
    if wf is not None:
        try:
            if len(string_remove) > 0:
                wf.write(outputString.replace(string_remove, ""))
            else:
                wf.write(outputString)
        except Exception as e:
            print("\n{0}e".format(e))
        #   wf.write(e)

def client_telnet(cn: ConnectionInformation, disable_log_output: bool, logdir_path: str):
    """
    Execute command list(TELNET)
    """
    # Start TELNET connection
    try:
        tn = telnetlib.Telnet(cn.host, cn.port, cn.timeout)
    except Exception as e:
        print(e)
        exit(0)

    if tn is None:
        print("Failed to connect ... {0}".format(cn.host))
        exit(0)

    wf = None
    if disable_log_output == False:
        # logfile open.
        wf = open(set_output_filename(cn, logdir_path), mode='wt')

    terminal = blessed.Terminal()

    while tn is not None:
        try:
            # Dealing with unread material.
            decoded_current_output = telnet_read_eager(tn, wf, None, enable_removeLF=True)
            if decoded_current_output == False:
                break

            # read keyboard inkey.
            with terminal.cbreak():
            #   time.sleep(0.01)
                readKey = terminal.inkey(timeout=0.001)
                if not readKey:
                    pass
                else:
                    # read key send.
                    tn.write(readKey.encode())
        except KeyboardInterrupt:
            pass

    # Dealing with unread material.
    while True:
        if tn.eof:
            break
        try:
            decoded_current_output = telnet_read_eager(tn, wf, None, enable_removeLF=True)
            if len(decoded_current_output) <= 0:
                break
        except:
            break

    if tn is not None:
        tn.close()
    if wf is not None:
        wf.close()

    return

def client_ssh(cn: ConnectionInformation, disable_log_output, logdir_path):
    """
    Execute command list(SSH)
    """
#   logger = paramiko.util.logging.getLogger()
#   paramiko.util.log_to_file("./log/paramiko_" + datetime.datetime.now().strftime('_%Y%m%d_%H%M%S') + ".log")

    cn.username = input("username : ")
    cn.password = getpass.getpass("password : ")

    # Start SSH connection
    error_count = 0

    while True:
        try:
            client = paramiko.SSHClient()
        #   client.set_missing_host_key_policy(paramiko.WarningPolicy())
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(cn.host, username = cn.username, password = cn.password)
            ssh_shell = client.invoke_shell()
        except Exception as e:
            print(e)
            error_count += 1
            if error_count >= 3:
                exit(0)
        else:
            break

    wf = None
    if disable_log_output == False:
        # logfile open.
        wf = open(set_output_filename(cn, logdir_path), mode='wt')

    terminal = blessed.Terminal()

    while ssh_shell.closed == False:
        try:
            if ssh_shell.recv_ready():
                # Dealing with unread material.
                current_output = ssh_shell.recv(65536 * 10)
                decoded_current_output = decode(current_output)
                print_and_write(decoded_current_output, wf)

            # read keyboard inkey.
            with terminal.cbreak():
                time.sleep(0.01)
                readKey = terminal.inkey(timeout=0.001)
                if not readKey:
                    pass
                else:
                    # key send.
                    ssh_shell.send(readKey)
        except KeyboardInterrupt:
            pass

    # Dealing with unread material.
    while True:
        try:
            current_output = ssh_shell.recv(65536 * 10)
            decoded_current_output = decode(current_output)
            print_and_write(decoded_current_output, wf)
            if len(decoded_current_output) <= 0:
                break
        except:
            break

    if ssh_shell is not None:
        ssh_shell.close()

    if wf is not None:
        wf.close()

    return

if __name__ == '__main__':
    main()
