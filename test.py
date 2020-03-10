import numpy as np

size_F = 11
size_A = 20
f_data =1
a_data =0

a = np.zeros(size_A*size_F)
a = a.reshape(size_A, size_F)

data = np.array ([[10,20,30,40,50,60,70,80,90,100,110],
              [-50,-45,-40,-30,-20,-10,-10,-10,-20,-30,-40]])

a[(size_A)-1] = data[a_data]
for x in range (0,size_F,1):
    temp = abs (data[1][x])
    for y in range (0,size_A,1):
        temp-=5
        if (temp) >= 0:
            pass
        else:
            a[y][x] = 1
            break

mas = []
for i in range (size_A):
    for j in range (size_F):
        mas[i][j].append(0)
        


