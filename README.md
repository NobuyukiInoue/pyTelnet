# PyTelnet

telnet/ssh client with automatic log saving function by Python3.

## Advance preparation

PyTelnet requires the following modules to be installed.

```
pip install blessed
pip install docopt
pip install paramiko
```

## Usage

```
 pyTelnet.py <host> [--port <port_num>] [--log_dir <logdir_path>] [--disable_log] [-h|--help]
 ```

## Options

Options:

|Options|Explanation|
|-------|-----------|
host|Destination hostname or IP address.
-p, --port \<port_num>|Destination Port Number. (default ... 23)<br>If 22 is specified, ssh communication will be selected.
-l, --log_dir \<logdir_path>|Specify the log output destination directory.(default="./log/")
-d, --disable_log|Do not output log file.
-h, --help|Show this help message and exit.

## Precautions

Even if the echo back is received after sending the keystrokes, tn.read_eager() and ssh_shell.recv() seem to be unable to detect the response until the buffer is empty and a newline is sent.


## logfile

If disable_log is not specified or false, the log file will be automatically created with the following naming convention.

```
./log/<host>_YYYYMMDD_hhmmss.log
```

Create the log directory in advance.


## Relation

* command_exec for TeraTerm<br>
https://www.vector.co.jp/soft/winnt/net/se516693.html

* PyTelnetCmdExec<br>
https://github.com/NobuyukiInoue/pyTelnetCmdExec

* PS_multiExec<br>
https://github.com/NobuyukiInoue/PS_multiExec

## Licence

[MIT](https://github.com/NobuyukiInoue/PyTelnet/blob/master/LICENSE)


## Author

[Nobuyuki Inoue](https://github.com/NobuyukiInoue/)
