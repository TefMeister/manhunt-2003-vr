import capstone
BASE=0x400000
p=r"D:\Program Files (x86)\Steam\steamapps\common\Manhunt\manhunt_module_unpacked.bin"
d=open(p,'rb').read()
md=capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
sites=[
(0x0042BDC3,"GetLastError",""),
(0x0043A005,"IsBadReadPtr","Broken SaveGame EntityData"),
(0x004667DC,"GetVersion","DropDeadBody Crash"),
(0x0046D688,"IsBadCodePtr","More Damage"),
(0x004732AA,"GetLastError","Broken Health 1"),
(0x00474EB7,"GetVersion","Ignore Control 1"),
(0x0047D05C,"IsBadWritePtr","Help Text Crash"),
(0x004C78A0,"GetVersion","Drop Item Timer"),
(0x004CC48C,"GetCurrentThread","Broken Doors"),
(0x004D26F4,"GetCurrentThread","Broken Health 2"),
(0x004D4063,"IsBadReadPtr","Broken Useables"),
(0x004D7E7A,"GetLastError","Broken Level Initialization 1"),
(0x004D84DE,"IsBadCodePtr","Broken Level Initialization 2"),
(0x004F222E,"IsBadWritePtr","Ignore Control 2"),
(0x004F9B5C,"IsBadReadPtr","Less Ammo"),
(0x005FFCE6,"GetVersion","Broken SaveGame Button"),
]
for i,(va,api,name) in enumerate(sites):
    pre=24; post=72
    start=va-pre
    code=d[start-BASE:start-BASE+pre+post]
    print("="*78)
    print("#%d  %-16s %-32s @ 0x%08X" % (i,api,name,va))
    print("-"*78)
    for ins in md.disasm(code, start):
        mark="  <== CALL" if ins.address==va else ""
        print("  %08X: %-24s %-8s %s%s" % (ins.address, ins.bytes.hex(' '), ins.mnemonic, ins.op_str, mark))
