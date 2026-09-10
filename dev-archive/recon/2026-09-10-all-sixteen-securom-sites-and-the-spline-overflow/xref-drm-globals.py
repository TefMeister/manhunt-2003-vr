import capstone, struct
BASE=0x400000
p=r"D:\Program Files (x86)\Steam\steamapps\common\Manhunt\manhunt_module_unpacked.bin"
d=open(p,'rb').read()
md=capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32)
def show(va,n=80,label=""):
    print("--- %s @ 0x%08X ---"%(label,va))
    code=d[va-BASE:va-BASE+n]
    for ins in md.disasm(code, va):
        print("  %08X: %-26s %-8s %s"%(ins.address, ins.bytes.hex(' '), ins.mnemonic, ins.op_str))
show(0x004667DC,90,"#2 DropDeadBody Crash (from call)")
print()
# also show 40 bytes before, aligned by scanning backwards for the magic-arg movs
print("raw bytes 0x004667B0..0x004667E0:", d[0x004667B0-BASE:0x004667E0-BASE].hex(' '))
print()
for g,name in [(0x00821540,"#14 Less Ammo global"),(0x0069B914,"#1 SaveGame EntityData global"),
               (0x007387A0,"#8 Broken Doors global"),(0x00739080,"#10 Broken Useables global"),
               (0x0073731C,"#7 Drop Item Timer global"),(0x00755978,"#11/#12 LevelInit global"),
               (0x007105A4,"#3 More Damage global"),(0x0069A5A0,"#0 unnamed global")]:
    pat=struct.pack("<I",g)
    hits=[]
    i=0
    while True:
        i=d.find(pat,i)
        if i<0: break
        hits.append(i+BASE)
        i+=1
    print("%-34s 0x%08X : %d refs  %s"%(name,g,len(hits),[hex(h) for h in hits[:14]]))
