mylist = list(range(20))
print(mylist)

for i in range(len(mylist) - 1):
    window = mylist[i:i + 2]
    print(window)
