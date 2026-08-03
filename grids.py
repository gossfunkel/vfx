
# square offset
for idx in range(NUM):
    pos[idx*2] = 6.*(idx%10) + ((idx/10)%2)*3. # x
    pos[idx*2+1] = 4.*(idx/10)                 # y