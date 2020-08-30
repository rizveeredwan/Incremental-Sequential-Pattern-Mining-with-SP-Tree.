from math import floor,log

value = 1<<47
xor = value ^ (value-1)
symbol = int(floor(log(xor,2)))
print(symbol)
