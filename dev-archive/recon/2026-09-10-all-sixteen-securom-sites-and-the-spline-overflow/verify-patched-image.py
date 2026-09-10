import capstone
BASE=0x400000
d=bytearray(open(r"D:\Program Files (x86)\Steam\steamapps\common\Manhunt\manhunt_module_unpacked.bin",'rb').read())
md=capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
P=[(0x0042BDCC,b"\xEB"),(0x0043A013,b"\x01"),(0x004667E7,b"\xEB"),(0x0046D6A2,b"\xEB"),
   (0x004732B5,b"\xEB"),(0x00474ED1,b"\xEB"),(0x004C78A9,b"\xEB"),(0x004CC46F,b"\x90"*10),
   (0x004D2701,b"\xEB"),(0x004D407D,b"\xEB"),(0x004D7E83,b"\xEB"),(0x004D84B8,b"\x00"),
   (0x004F2245,b"\xEB"),(0x004F9B62,b"\x90"*6),(0x005FFCF1,b"\xEB")]
for va,b in P: d[va-BASE:va-BASE+len(b)]=b
def show(va,n,label):
    print("--- AFTER PATCH: %s ---"%label)
    for ins in md.disasm(bytes(d[va-BASE:va-BASE+n]), va):
        print("  %08X: %-22s %-7s %s"%(ins.address, ins.bytes.hex(' '), ins.mnemonic, ins.op_str))
    print()
show(0x004CC466,0x3C,"#8 Broken Doors")
show(0x004F9B57,0x24,"#14 Less Ammo")
show(0x004D84B0,0x14,"#12 Level Init 2")
show(0x0043A00B,0x14,"#1 SaveGame EntityData")
show(0x0042BDC9,0x22,"#0 unnamed")
