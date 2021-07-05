#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Run a Raspberry PI OS image with Docker to install Nimbus-Userland specific
apt packages.
"""
import sys
import pexpect
import customise_os


def install_nimbus_apt_dependencies(child):
    child.sendline("df -h")
    child.expect_exact(customise_os.BASH_PROMPT)
    child.sendline("sudo apt-get update -qq")
    child.expect_exact(customise_os.BASH_PROMPT)
    # Break down the install in multiple commands to kee the time per command low 
    child.sendline("sudo apt-get install -y git cmake")
    child.expect_exact(customise_os.BASH_PROMPT)
    child.sendline(
        "sudo apt-get install -y libxmlsec1-dev libxml2 libxml2-dev libxkbcommon-x11-0 libatlas-base-dev libcurl4-openssl-dev libmicrohttpd-dev libjsoncpp-dev libjsonrpccpp-dev libargtable2-dev libhiredis-dev libi2c-dev libssl-dev libboost-all-dev"
    )
    child.expect_exact(customise_os.BASH_PROMPT, timeout=15*60)
    child.sendline("echo 'dtoverlay=irs1125' | sudo tee -a /boot/config.txt")
    child.expect_exact(customise_os.BASH_PROMPT)
    child.sendline("echo 'deb http://apt.pieye.org/debian/ nimbus-stable main' | sudo tee -a /etc/apt/sources.list")
    child.expect_exact(customise_os.BASH_PROMPT)
    child.sendline("wget -O - -q http://apt.pieye.org/apt.pieye.org.gpg.key | sudo apt-key add -")
    child.expect_exact(customise_os.BASH_PROMPT)
    child.sendline("sudo apt-get update -qq")
    child.expect_exact(customise_os.BASH_PROMPT)
    child.sendline("sudo apt-get -y install nimbus-server")
    child.expect_exact(customise_os.BASH_PROMPT)
    child.sendline("df -h")
    child.expect_exact(customise_os.BASH_PROMPT)
    
    
    

def run_edits(img_path, needs_login=True):
    print("Staring Raspberry Pi OS Nimbus customisation: {}".format(img_path))

    try:
        child, docker_container_name = customise_os.launch_docker_spawn(img_path)
        if needs_login:
            customise_os.login(child)
        else:
            child.expect_exact(customise_os.BASH_PROMPT)
        install_nimbus_apt_dependencies(child)
        # We are done, let's exit
        child.sendline("sudo shutdown now")
        child.expect(pexpect.EOF)
        child.wait()
    # Let ay exceptions bubble up, but ensure clean-up is run
    finally:
        customise_os.close_container(child, docker_container_name)


if __name__ == "__main__":
    # We only use the first argument to receive a path to the .img file
    run_edits(sys.argv[1])
