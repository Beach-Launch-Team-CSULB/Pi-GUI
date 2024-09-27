import bitstring
from bitarray.util import ba2int
from bitarray import bitarray

bitval = "1111111111111111111111111111111111111111011110101110010111000101"
hexval = "ffffffffff7ae5c5"
va11= ba2int(bitarray(bitval), signed = True)/1000000
val2 = int(hexval, base=16)/1000000
print(va11)
print(val2)