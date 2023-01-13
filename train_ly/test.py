lst = [1,2,3,None, 4,5,6]
for i in lst:
    if i is None:
        continue
    print(i) 
print("done")