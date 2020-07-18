from collections import deque
Q1 = deque([1,2,3])
Q2 = Q1.copy()
print(Q2)
Q2.append(4)
print(Q1)
print(Q2)
