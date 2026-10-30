"""disasm.py ADDR N: disassemble N bytes of the running game (32-bit)."""
import sys, capstone
from mem import rd
a, n = int(sys.argv[1], 16), int(sys.argv[2])
for i in capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_32).disasm(rd(a, n), a): print(f"{i.address:#x}: {i.mnemonic} {i.op_str}")
