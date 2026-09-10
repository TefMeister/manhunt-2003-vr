import capstone
BASE=0x400000
p=r"D:\Program Files (x86)\Steam\steamapps\common\Manhunt\manhunt_module_unpacked.bin"
d=open(p,'rb').read()
md=capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
def show(va,n,label):
    print("--- %s : 0x%08X ---"%(label,va))
    for ins in md.disasm(d[va-BASE:va-BASE+n], va):
        print("  %08X: %-24s %-7s %s"%(ins.address, ins.bytes.hex(' '), ins.mnemonic, ins.op_str))
    print()
show(0x004CC450,0x40,"#8 Broken Doors - what precedes the DRM block")
show(0x004CBEC0,0x30,"#8 the OTHER reader of 0x7387A0")
show(0x004F9B20,0x40,"#14 Less Ammo - what precedes")
show(0x004F9BFC,0x60,"#14 Less Ammo - later uses")
show(0x0043A8E0,0x40,"#1 the OTHER reader of 0x69B914")
show(0x004D3860,0x40,"#10 the OTHER reader of 0x739080")
