# encoding: utf-8
import sys
import os
import subprocess


def main(args):
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags = subprocess.CREATE_NEW_CONSOLE | subprocess.STARTF_USESHOWWINDOW
    startupinfo.wShowWindow = subprocess.SW_HIDE
    process = subprocess.Popen("notepad.exe", startupinfo=startupinfo)

    print(process)


if __name__ == '__main__':
    main(sys.argv[1:])
