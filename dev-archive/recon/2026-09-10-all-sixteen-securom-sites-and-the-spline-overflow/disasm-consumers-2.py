import capstone
BASE=0x400000
d=open(r"D:\Program Files (x86)\Steam\steamapps\common\Manhunt\manhunt_module_unpacked.bin",'rb').read()
md=capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
def show(va,n,label):
    print("--- %s : 0x%08X ---"%(label,va))
    for ins in md.disasm(d[va-BASE:va-BASE+n], va):
        print("  %08X: %-22s %-7s %s"%(ins.address, ins.bytes.hex(' '), ins.mnemonic, ins.op_str))
    print()
show(0x004D8620,0x24,"0x755978 ref at 0x4d8627")
show(0x004D4030,0x38,"#10 block gate at 0x4d403e")
show(0x004C7610,0x20,"#7 DropItemTimer reader 0x4c7619")
show(0x004C7018,0x20,"#4/#9 Health reader 0x4c7022")
show(0x00492208,0x20,"#5/#13 IgnoreControl reader 0x49220f")
show(0x005FFBF8,0x18,"#15 SaveGameButton ref 0x5ffc01")
