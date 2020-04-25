
import mmap

with open("FireRed.gba", "rb") as f:
    mm = mmap.mmap(f.fileno(), 0)
    print(mm.read(10))
