aa = "+552.25 -502 +656"

arr = aa.split(' ')
for i in range(len(arr)):
    if arr[i].isdecimal():
        arr[i] = float(arr[i])
    elif arr[i].isnumeric():
        arr[i] = int(arr[i])
print(arr)
