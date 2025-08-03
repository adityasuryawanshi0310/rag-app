inp = int(input())
arr = list(map(int , input().split()))
c = 0
n = len(arr)-1
if arr[n]<9:
    arr[n]+=1
   
else:
    j = n
    while(j>=0):
        num = arr[j]+c
        if num<9:
            arr[j] = num
            c=0
            break
        else:
            arr[j] = 0
            c = 1
        j-=1    
    if c==1:
        arr.insert(0,1)
s =" ".join(map(str,arr))
print(s)
        
    