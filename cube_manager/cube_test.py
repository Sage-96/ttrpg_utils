from dataclasses import dataclass
from typing import Any,List,Tuple
from math import factorial
from random import randint

@dataclass
class Room:
    start_x:int
    start_y:int
    _id:str
    
    def __post_init__(self):
        self.start=(self.start_x,self.start_y)
    
    def __repr__(self):
        return self._id
    
rooms={}
i=0
size=8

for x in range(size):
    for y in range(size):
        rooms[(x,y)]=Room(x,y,f'{i:0>{len(str(size**2-1))}} ')
        i+=1

def shift_row(room_dict:dict[tuple[int,int],Room],r:int,d:int=1)->dict[tuple[int,int],Room]:
    #print(f'Shifting row {r} {d}')
    room_dict=room_dict.copy()
    if d not in {1,-1}:
        return
    
    dim=max([rm[1] for rm in rooms.keys() if rm[0]==r])
    if d==1:
        temp=room_dict[(r,dim)]
        for c in range(dim,0,-1):
            room_dict[(r,c)]=room_dict[(r,c-1)]
        room_dict[r,0]=temp
    else:
        temp=room_dict[(r,0)]
        for c in range(0,dim):
            room_dict[(r,c)]=room_dict[(r,c+1)]
        room_dict[r,dim]=temp
    return room_dict
def shift_col(room_dict:dict[tuple[int,int],Room],c:int,d:int=1)->dict[tuple[int,int],Room]:
    #print(f'Shifting col {c} {d}')
    room_dict=room_dict.copy()
    if d not in {1,-1}:
        return
    
    dim=max([rm[0] for rm in rooms.keys() if rm[1]==c])
    if d==1:
        temp=room_dict[(dim,c)]
        for r in range(dim,0,-1):
            room_dict[(r,c)]=room_dict[(r-1,c)]
        room_dict[0,c]=temp
    else:
        temp=room_dict[(0,c)]
        for r in range(0,dim):
            room_dict[(r,c)]=room_dict[(r+1,c)]
        room_dict[dim,c]=temp
    return room_dict

def show_room(room):
    show=''
    for row in range(max([rm[0] for rm in rooms.keys()])+1):
        for col in range(max([rm[1] for rm in rooms.keys()])+1):
            show+=room[(row,col)].__repr__()
        show+='\n'
    print(show)

'''
for row in range(max([rm[0] for rm in rooms.keys()])+1):
    show_room(shift_row(rooms,row,1))
for col in range(max([rm[1] for rm in rooms.keys()])+1):
    show_room(shift_col(rooms,col,1))'''

mx_r=max([rm[0] for rm in rooms.keys()])+1
mx_c=max([rm[1] for rm in rooms.keys()])+1

fxns=[lambda t,pt=y,dr=z: shift_row(t,pt,dr) for y in range(size) for z in (-1,1)]+\
     [lambda t,pt=y,dr=z: shift_col(t,pt,dr) for y in range(size) for z in (-1,1)]

fxnl=len(fxns)
to_shift=rooms.copy()
history=[]
been_orig=False
for _ in range(10_000_000):
    rand=randint(0,fxnl-1)
    history.append(rand)
    to_shift=fxns[rand](to_shift)
    delta=[(k,rooms[k],to_shift[k]) for k in rooms.keys() if rooms[k]!=to_shift[k]]
    if len(delta)<size and len(delta)!=0:
        print(f'\033[91mSHORT DISCREPANCY {len(delta)=}. EXAMINE HISTORY.\033[0m')
        break
    elif len(delta)==0:
        print(f'\033[92mReturn to base state after {len(history)}.\033[0m')
        been_orig=True
    #elif len(delta)%size!=0:
        #print(f'\033[93mDiscrepancy not multiple of size. {len(delta)=}\033[0m')
    #elif len(delta)==size**2:
        #print(f'\033[93mFully displaced. {len(delta)=}\033[0m')        
    if _%100000==0:print(f'{_:_}')
while not been_orig or True:
    _+=1
    rand=randint(0,fxnl-1)
    history.append(rand)
    to_shift=fxns[rand](to_shift)
    delta=[(k,rooms[k],to_shift[k]) for k in rooms.keys() if rooms[k]!=to_shift[k]]
    if len(delta)<size and len(delta)!=0:
        print(f'\033[91mSHORT DISCREPANCY {len(delta)=}. EXAMINE HISTORY.\033[0m')
        break
    elif len(delta)==0:
        print(f'\033[92mReturn to base state.\033[0m')
        been_orig=True
    #elif len(delta)%size!=0:
        #print(f'\033[93mDiscrepancy not multiple of size. {len(delta)=}\033[0m')
    #elif len(delta)==size**2:
        #print(f'\033[93mFully displaced. {len(delta)=}\033[0m')        
    if _%100000==0:print(f'{_:_}')
    
        
        
    
    




'''
queue=[rooms]
done=[]
while queue:
    nxt=queue.pop()
    
    for row in range(mx_r):
        tmp=shift_row(nxt,row,1)
        if tmp not in queue and tmp not in done:
            queue.append(tmp.copy())
        tmp=shift_row(nxt,row,-1)
        if tmp not in queue and tmp not in done:
            queue.append(tmp.copy())    
    for col in range(mx_c):
        tmp=shift_col(nxt,col,1)
        if tmp not in queue and tmp not in done:
            queue.append(tmp.copy())
        tmp=shift_col(nxt,col,-1)
        if tmp not in queue and tmp not in done:
            queue.append(tmp.copy())
    done.append(nxt.copy())
    
    if len(queue)%100==0:
        print(f'Queue length:{len(queue)}')
    if len(done)%1000==0:
        print(f'Finished length:{len(done)}')

print(f'Possible states: {len(done)}\nExpected value: {factorial(size**2)}\n{"Pass" if len(done)==factorial(size**2) else "Fail"}')
'''
    