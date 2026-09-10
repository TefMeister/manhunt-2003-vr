BASE=0x400000
d=open(r"D:\Program Files (x86)\Steam\steamapps\common\Manhunt\manhunt_module_unpacked.bin",'rb').read()
def by(va,n): return d[va-BASE:va-BASE+n]
def carr(name,b):
    return "static const BYTE %s[] = { %s };"%(name, ", ".join("0x%02X"%x for x in b))
# (tag, callva, patchva, writelen, newbytes, verifylen, sitename, why)
S=[
("s00",0x0042BDC3,0x0042BDCC,1,b"\xEB",12,"(unnamed) GetLastError @0x0042BDC3",
 "takes the game's own pass branch: [0x0069A5A0] = 0x1F instead of 0 (0 makes its reader bail out early)"),
("s01",0x0043A005,0x0043A013,1,b"\x01",10,"Broken SaveGame EntityData: IsBadReadPtr @0x0043A005",
 "restores [0x0069B914] = 1 (its static value) instead of 0, so the entity-0x25 size adjustment still happens"),
("s02",0x004667DC,0x004667E7,1,b"\xEB",12,"DropDeadBody Crash: GetVersion @0x004667DC",
 "takes the game's own pass branch: [0x00756244] = 0 instead of 2"),
("s03",0x0046D688,0x0046D6A2,1,b"\xEB",12,"More Damage: IsBadCodePtr @0x0046D688",
 "skips 'mov [0x007105A4], 0'; leaving it at 1 makes its reader skip the damage multiply"),
("s04",0x004732AA,0x004732B5,1,b"\xEB",12,"Broken Health 1: GetLastError @0x004732AA",
 "skips 'mov [0x00755E50], 1'; its reader bails out on any non-zero"),
("s05",0x00474EB7,0x00474ED1,1,b"\xEB",12,"Ignore Control 1: GetVersion @0x00474EB7",
 "takes the game's own pass branch: [0x0075625C] = 1 instead of 2"),
("s08",0x004CC48C,0x004CC46F,10,b"\x90"*10,16,"Broken Doors: GetCurrentThread @0x004CC48C",
 "stops the block NULLing the live pointer in [0x007387A0]; the stub used to put it back"),
("s09",0x004D26F4,0x004D2701,1,b"\xEB",12,"Broken Health 2: GetCurrentThread @0x004D26F4",
 "skips 'mov [0x00755E50], 2'; its reader bails out on any non-zero"),
("s10",0x004D4063,0x004D407D,1,b"\xEB",12,"Broken Useables: IsBadReadPtr @0x004D4063",
 "takes the game's own pass branch: [0x00739080] = 1 instead of 0 (0 makes its reader return failure)"),
("s11",0x004D7E7A,0x004D7E83,1,b"\xEB",12,"Broken Level Initialization 1: GetLastError @0x004D7E7A",
 "takes the game's own pass branch: [0x00755978] = 0 instead of 1 (1 makes its reader bail out)"),
("s12",0x004D84DE,0x004D84B8,1,b"\x00",14,"Broken Level Initialization 2: IsBadCodePtr @0x004D84DE",
 "writes 0 not 1 into [0x00755978]; the stub used to overwrite the 1, and 1 makes the reader bail out"),
("s13",0x004F222E,0x004F2245,1,b"\xEB",12,"Ignore Control 2: IsBadWritePtr @0x004F222E",
 "skips 'mov [0x0075625C], 2'; 2 makes its reader zero [0x00725710]"),
("s14",0x004F9B5C,0x004F9B62,6,b"\x90"*6,12,"Less Ammo: IsBadReadPtr @0x004F9B5C",
 "stops the block decrementing [0x00821540] back to 0; at 1 the ammo drain and the divide-by-2 are both no-ops"),
("s15",0x005FFCE6,0x005FFCF1,1,b"\xEB",12,"Broken SaveGame Button: GetVersion @0x005FFCE6",
 "takes the game's own pass branch: [0x007D6148] = 0x2E instead of 0x2D (its reader tests for 0x2E)"),
]
out=[]
tab=[]
for tag,callva,pva,wl,new,vl,name,why in S:
    exp=by(pva,vl)
    assert len(exp)==vl
    out.append(carr(tag+"_expect",exp))
    out.append(carr(tag+"_patch",new))
    tab.append('    { "%s", 0x%08X,\n      %s_expect, %s_patch, %d, sizeof(%s_expect),\n      "%s" },'
               %(name,pva,tag,tag,wl,tag,why))
print("\n".join(out))
print()
print("\n".join(tab))
