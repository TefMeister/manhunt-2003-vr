import capstone
BASE=0x400000
d=open(r"D:\Program Files (x86)\Steam\steamapps\common\Manhunt\manhunt_module_unpacked.bin",'rb').read()
md=capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
def show(va,n,label):
    print("--- %s : 0x%08X ---"%(label,va))
    for ins in md.disasm(d[va-BASE:va-BASE+n], va):
        print("  %08X: %-22s %-7s %s"%(ins.address, ins.bytes.hex(' '), ins.mnemonic, ins.op_str))
    print()
show(0x00471C90,0x50,"callee 0x471C90 (does it preserve EBX?)")
show(0x004720C8,0x40,"writer region A")
show(0x00472148,0x60,"writer region B")
show(0x004721E8,0x60,"writer region C")
