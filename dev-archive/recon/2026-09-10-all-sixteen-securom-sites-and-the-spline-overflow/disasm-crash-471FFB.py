import capstone
BASE=0x400000
d=open(r"D:\Program Files (x86)\Steam\steamapps\common\Manhunt\manhunt_module_unpacked.bin",'rb').read()
md=capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
def show(va,n,label):
    print("--- %s : 0x%08X ---"%(label,va))
    for ins in md.disasm(d[va-BASE:va-BASE+n], va):
        m=" <== CRASH" if ins.address==0x00471FFB else ""
        print("  %08X: %-24s %-7s %s%s"%(ins.address, ins.bytes.hex(' '), ins.mnemonic, ins.op_str, m))
    print()
show(0x00471F90,0xA0,"crash site 0x00471FFB")
show(0x00791F00,0x60,"caller 0x00791F2C")
