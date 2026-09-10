import capstone, struct
BASE=0x400000
p=r"D:\Program Files (x86)\Steam\steamapps\common\Manhunt\manhunt_module_unpacked.bin"
d=open(p,'rb').read()
md=capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
def show(va,n,label):
    print("--- %s : 0x%08X ---"%(label,va))
    for ins in md.disasm(d[va-BASE:va-BASE+n], va):
        print("  %08X: %-22s %-7s %s"%(ins.address, ins.bytes.hex(' '), ins.mnemonic, ins.op_str))
    print()
# consumers
show(0x004D84A8,0x30,"#12 LevelInit - block start 0x755978")
show(0x004D8618,0x28,"#12/#11 LevelInit - reader 0x4d8627")
show(0x004D7E50,0x20,"#11 LevelInit - reader 0x4d7e61")
show(0x0046B040,0x28,"#3 More Damage - reader 0x46b04f")
show(0x00429B54,0x28,"#0 unnamed - reader 0x429b63")
show(0x0042BC84,0x24,"#0 unnamed - reader 0x42bc92")
# 0x75625C (#5/#13), 0x755E50 (#4/#9), 0x7D6148 (#15), 0x756244 (#2), 0x73731C (#7)
for g,name in [(0x0075625C,"IgnoreControl"),(0x00755E50,"Health"),(0x007D6148,"SaveGameButton"),
               (0x00756244,"DropDeadBody"),(0x0073731C,"DropItemTimer")]:
    pat=struct.pack("<I",g); hits=[]; i=0
    while True:
        i=d.find(pat,i)
        if i<0: break
        hits.append(i+BASE); i+=1
    print("%-16s 0x%08X refs: %s"%(name,g,[hex(h) for h in hits]))
print()
print("static values in dump:")
for g in (0x0069B914,0x00755978,0x007387A0,0x00821540,0x00739080):
    print("  0x%08X = 0x%08X"%(g, struct.unpack("<I", d[g-BASE:g-BASE+4])[0]))
