import random
from math import inf
import numpy as np
from itertools import product
from typing import Any, Tuple
from dataclasses import dataclass, field
from PIL import Image
from datetime import datetime
import os

class Dungeon:
    _maskmap={0:1,1:2,2:3,4:4,8:5,16:6,32:7,64:8,128:9,3:2,5:10,9:11,17:12,33:13,
              65:14,129:2,6:4,10:15,18:16,34:17,66:18,130:19,12:4,20:20,36:21,68:22,
              132:23,24:6,40:24,72:25,136:26,48:6,80:27,144:28,96:8,160:29,192:8,7:30,
              11:11,19:12,35:13,67:14,131:2,13:10,21:31,37:32,69:33,133:10,25:12,41:34
              ,73:35,137:11,49:12,81:36,145:12,97:14,161:13,193:37,14:4,22:20,38:21,
              70:22,134:38,26:16,42:39,74:40,138:41,50:16,82:42,146:43,98:18,162:44,
              194:18,28:45,44:21,76:22,140:23,52:20,84:46,148:47,100:22,164:52,196:22,
              56:6,88:27,152:28,104:25,168:51,200:25,112:50,176:28,208:27,224:8,15:30,
              23:49,39:48,71:53,135:30,27:12,43:34,75:35,139:11,51:12,83:36,147:12,
              99:14,163:13,195:37,29:54,45:32,77:33,141:10,53:54,85:59,149:31,101:33,
              165:32,197:58,57:12,89:56,153:12,105:35,169:34,201:57,113:56,177:12,
              209:55,225:37,30:45,46:21,78:22,142:23,54:20,86:46,150:47,102:22,166:52,
              198:22,58:16,90:42,154:43,106:40,170:83,202:40,114:76,178:43,210:42,
              226:18,60:45,92:74,156:71,108:22,172:52,204:22,116:77,180:47,212:46,
              228:22,120:50,184:28,216:27,232:25,240:50,241:67,242:76,244:77,248:50,
              115:56,117:82,121:56,118:77,122:76,124:65,179:12,181:31,185:12,182:47,
              186:43,188:71,55:49,59:12,61:54,62:45,211:55,213:81,217:55,214:46,218:42
              ,220:74,87:80,91:36,93:79,94:74,151:49,155:12,157:54,158:71,31:63,227:37
              ,229:58,233:57,230:22,234:40,236:22,103:53,107:35,109:33,110:22,167:48,
              171:34,173:48,174:52,47:48,199:61,203:57,205:58,206:22,79:53,143:30,
              243:67,245:78,249:67,246:77,250:76,252:65,119:69,123:56,125:70,126:65,
              183:49,187:12,189:54,190:71,63:63,215:72,219:55,221:73,222:74,95:75,
              159:63,231:61,235:57,237:58,238:22,111:53,175:48,207:61,247:68,251:67,
              253:66,254:65,127:64,191:63,223:62,239:61,255:60}
    
    @dataclass
    class Cell:
        x:int
        y:int
        cell_type:str='Cross'
        height:int=1
        width:int=1
        ul_corner:tuple[int,int]=(2,2)
        connections:list=field(default_factory=lambda:[])
        merges:list=field(default_factory=lambda:[])
        connectionmap:set=field(default_factory=lambda:set())
        
        
        def mark_as_room(self):
            self.cell_type='Room'
        def set_corner(self,x:int,y:int):
            self.ul_corner = (x,y)
        def set_size(self,width:int,height:int):
            self.width,self.height=width,height
        
            
    
    def __init__(self,cell_count:tuple[int,int]=(4,3),map_size:tuple[int,int]=(96,39),mode:int=0,density:float=0.6, merge_chance:float=0.05,search_range:int=1,**kwargs):
        
        self.map_width, self.map_height = map_size
        self.map_width=int(self.map_width)
        self.map_height=int(self.map_height)
        
        self.map_size=map_size
        self.columns, self.rows = cell_count
        self.columns=int(self.columns)
        self.rows=int(self.rows)
        if self.map_height<10*self.rows:
            print(f'fixing height:{self.map_height} to {10*self.rows}')
            self.map_height=10*self.rows
        if self.map_width<12*self.columns:
            print(f'fixing width:{self.map_width} to {12*self.columns}')
            self.map_width=12*self.columns
            
        self.mode=int(mode)
        self.density=density
        self.merge_chance=merge_chance
        self.search_range=search_range
        
        self.kwargs=kwargs
        
        self.extra_walk_count=int(self.kwargs.get('extra_walk_count',0))
        self.extra_walk_length=int(self.kwargs.get('extra_walk_length',100))
        
        self.count=self.columns*self.rows
        self.room_count=int(self.count*density)+ random.randint(0,2)
        self.room_width=self.map_width//self.columns
        self.room_height=self.map_height//self.rows
        
        
        self.cells={}
        self.rooms={}

        self.map_=np.full((self.map_height,self.map_width),'W',dtype="U64")
                
        self.setup()
        self.cull_cells()
        self.make_connections()
        self.make_map()
        for _ in range(self.extra_walk_count):
            self.random_path_walk()
        
        
        
        #self.show()
        
        
    def setup(self):
        
        for x,y in product(range(self.columns),range(self.rows)):
            self.cells[(x,y)]=(self.Cell(x,y))
        cell_list=list(self.cells.values())
        random.shuffle(cell_list)
        for i in range(self.room_count):
            cell=cell_list[i]
            cell.mark_as_room()
            x=cell.x
            y=cell.y
            
            self.rooms[(x,y)]=(cell)
        
        max_room_width=self.room_width-4
        max_room_height=self.room_height-3
        
        for pos,cell in self.cells.items():
            
            cell.connectionmap=set([pos])
            
            if cell.cell_type == "Room":
                local_room_width = (random.randint(5,max_room_width-1) if max_room_width-1>=5 else max_room_width-1)
                local_room_height= (random.randint(4,max_room_height-1) if max_room_height-1>=4 else max_room_height-1)
                
                local_room_height=min(local_room_height, int(local_room_width*1.5))
                local_room_width=min(local_room_width, int(local_room_height*1.5))
                x_offset = random.randint(0,max_room_width-local_room_width-1)
                y_offset = random.randint(0,max_room_height-local_room_height-1)
                
                local_x,local_y=cell.ul_corner
                cell.set_corner(local_x+x_offset,local_y+y_offset)
                cell.set_size(local_room_width,local_room_height)
            elif cell.cell_type == "Cross":
                local_x,local_y=cell.ul_corner
                max_x_offset=(max_room_width-4 if max_room_width-4>=0 else 0)
                max_y_offset=(max_room_height-3 if max_room_height-3>=0 else 0)
                left_margin=(1 if cell.x==0 else 2)
                right_margin=(2 if cell.x==self.columns else 2)
                top_margin=(1 if cell.y==0 else 2)
                bottom_margin=(1 if cell.y==self.rows else 2)
                local_x=random.randint(local_x+left_margin,local_x+max_x_offset-right_margin)
                local_y=random.randint(local_y+top_margin,local_y+max_y_offset-bottom_margin)
                cell.set_corner(local_x,local_y)
                
    def cull_cells(self):
        '''
        Modes:
        0: Default, full map
        
        6: Cull specific cells - USE WITH CAUTION, CAN CAUSE DISCONNECTED BLOCKS
        '''
        if self.mode==0:
            return
        if self.mode==6:
            to_remove=self.kwargs.get('cull',[])
            for c in to_remove:
                self.cells.pop(c,None)
            return
        
    
    def make_connections(self):
        possible_connections=[]
        for cell in self.cells:
            lx,ly=cell
            
            cx=lx
            while cx<self.columns and (cx-lx)<=self.search_range:
                cx+=1
                if (cx,ly) in self.cells:
                    possible_connections.append(((lx,ly),(cx,ly)))
                    break
            
            cy=ly
            while cy<self.rows and (cy-ly)<=self.search_range:
                cy+=1
                if (lx,cy) in self.cells:
                    possible_connections.append(((lx,ly),(lx,cy)))
                    break
        
        target_cellset = set(self.cells.keys())
        check_cell=list(target_cellset)[0]
        random.shuffle(possible_connections)
        bonus_connections=int(self.kwargs.get('bonus_connections',0))
        extra_passes=0
        while possible_connections:
            a,b=possible_connections.pop()
            merge_roll=random.random()
            if merge_roll<self.merge_chance:
                self.cells[a].merges.append(b)
            else:
                self.cells[a].connections.append(b)
            
            new_connectionmap=self.cells[a].connectionmap|self.cells[b].connectionmap
            for cell in new_connectionmap:
                self.cells[cell].connectionmap = new_connectionmap
            
            if self.cells[check_cell].connectionmap == target_cellset:
                if extra_passes>=bonus_connections:
                    return
                extra_passes+=1
        return
            
                
            
    def make_map(self):
        for (x,y),cell in self.cells.items():
            dx,dy=cell.width,cell.height
            ox,oy = cell.ul_corner
            ox+=x*self.room_width
            oy+=y*self.room_height
            for row in range(oy,oy+dy):
                for col in range(ox,ox+dx):
                    self.map_[row,col]=' '
            
            for path in cell.connections:
                bx,by=path
                b=self.cells[path]
                dbx,dby=b.width,b.height
                obx,oby=b.ul_corner
                obx+=bx*self.room_width
                oby+=by*self.room_height
                midpoints=1
                
                if y==by:#horizontal
                    l_ep = random.randint(oy,oy+dy-1)
                    r_ep = random.randint(oby,oby+dby-1)
                    d=(r_ep-l_ep)//abs(r_ep-l_ep) if r_ep != l_ep else 0
                    mp=random.randint(ox+dx,obx)
                    track_x,track_y=ox+dx-1,l_ep
                    
                    while track_x<=mp:
                        track_x+=1
                        self.map_[track_y,track_x]=' '
                    while track_y!=r_ep:
                        track_y+=d
                        self.map_[track_y,track_x]=' '
                    while track_x<obx:
                        track_x+=1
                        self.map_[track_y,track_x]=' '
                    
                    
                elif x==bx:#vertical
                    t_ep = random.randint(ox,ox+dx-1)
                    b_ep = random.randint(obx,obx+dbx-1)
                    d=(b_ep-t_ep)//abs(b_ep-t_ep) if b_ep != t_ep else 0
                    mp=random.randint(oy+dy,oby)
                    track_y,track_x=oy+dy-1,t_ep
                    
                    while track_y<=mp:
                        track_y+=1
                        self.map_[track_y,track_x]=' '
                    while track_x!=b_ep:
                        track_x+=d
                        self.map_[track_y,track_x]=' '
                    while track_y<oby:
                        track_y+=1
                        self.map_[track_y,track_x]=' '
                        
            for merge in cell.merges:
                #print(f'Merge ({x},{y}):{path}')
                bx,by=merge
                b=self.cells[path]
                dbx,dby=b.width,b.height
                obx,oby=b.ul_corner
                obx+=bx*self.room_width
                oby+=by*self.room_height
                midpoints=1
                
                if y==by:#horizontal
                    #print('H')
                    l_end=ox
                    #print(f'{l_end=}')
                    r_end=obx+dbx
                    #print(f'{r_end=}')
                    t_end=min(oy,oby)
                    #print(f'{t_end=}')
                    b_end=max(oy+dy,oby+dby)
                    #print(f'{b_end=}')
                    for row in range(t_end,b_end):
                        for col in range(l_end,r_end):
                            self.map_[row,col]=' '

                elif x==bx:#vertical
                    #print('V')
                    t_end=oy
                    b_end=oby+dby
                    l_end=min(ox,obx)
                    r_end=max(ox+dx,obx+dbx)
                    #print(f'{l_end:}')
                    #print(f'{r_end:}')
                    #print(f'{t_end:}')
                    #print(f'{b_end:}')
                    for row in range(t_end,b_end):
                        for col in range(l_end,r_end):
                            self.map_[row,col]=' '
                
            
        for row in range(0,self.map_height):
            self.map_[row,0]='x'
            self.map_[row,self.map_width-1]='x'
        for col in range(0,self.map_width):
            self.map_[0,col]='x'
            self.map_[self.map_height-1,col]='x'
        
    def random_path_walk(self):
        directions={0:(-1,0),1:(0,1),2:(1,0),3:(0,-1)}
        x,y=0,0
        while self.map_[y,x]!=' ':
            x=random.randint(1,self.map_width-2)
            y=random.randint(1,self.map_height-2)
        path_length=0
        facing=random.randint(0,3)
        
        while path_length<=self.extra_walk_length:
            segment_length=random.randint(3,7)
            dx,dy=directions[facing]
            for _ in range(segment_length):
                x+=dx
                y+=dy
                
                if x>=self.map_width-1 or x<=0:
                    return
                if y>=self.map_height-1 or y<=0:
                    return
                self.map_[y,x]=' '
                path_length+=1
            facing=(facing+random.choice((-1,1)))%4
            
        return
            
            
    
    def show_cell_boundaries(self):
        self.map_colored=self.map_.copy()
        for (x,y),cell in self.cells.items():
            if x%2==y%2:
                color='\x1b[94m'
            else:
                color='\x1b[95m'
            suffix='\x1b[0m'
            ox=x*self.room_width
            oy=y*self.room_height
            dx=self.room_width
            dy=self.room_height
            for row in range(oy,oy+dy):
                for col in range(ox,ox+dx):
                    self.map_colored[row,col]=color+self.map_[row,col]+suffix
        self.show(param=1)
            
        
        
        
    def show(self,param=0):
        if param==0:to_show=self.map_
        elif param==1:to_show=self.map_colored
        for line in to_show:
            print(''.join(list(map(str,line))))
        print('\n')
        
    def render(self):
        border=Image.open('assets/border.png')
        wall=Image.open('assets/wall.png')
        floor=Image.open('assets/floor.png')
        tiles={' ':floor,'W':wall,'x':border}
        tile_size=border.width
        
        final=Image.new('RGB',(self.map_width*tile_size,self.map_height*tile_size))
        for (y,x),ch in np.ndenumerate(self.map_):
            pos=(x*tile_size,y*tile_size)
            final.paste(tiles[ch],pos)
        final.save(f'maps/dun_gen_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png')
    def render_thumbnail(self):
        
        pixels={' ':(75,105,47),'W':(105,106,106),'x':(52,52,52)}
        
        thumbnail=Image.new('RGB',(self.map_width,self.map_height))
        for (y,x),ch in np.ndenumerate(self.map_):
            thumbnail.putpixel((x,y),pixels[ch])
        return thumbnail
        
        return thumbnail
        
    def fancy_render(self):
        border=Image.open('assets/border.png').convert('RGBA')
        wall=Image.open('assets/wall.png').convert('RGBA')
        floor=Image.open('assets/floor.png').convert('RGBA')
        wall_floor=Image.open('assets/wall_floor.png').convert('RGBA')
        tiles={' ':floor,'W':wall,'x':border}
        tile_size=border.width
        
        mask_file=Image.open('assets/tileset_mask.png').convert('L')
        masks={}        
        for x in range(0,mask_file.width//tile_size):
            l=x*tile_size
            r=l+tile_size
            t=0
            b=tile_size
            masks[x]=mask_file.crop((l,t,r,b))
        
        final=Image.new('RGBA',(self.map_width*tile_size,self.map_height*tile_size))
        for (y,x),ch in np.ndenumerate(self.map_):
            pos=(x*tile_size,y*tile_size)
            if ch !='W':
                final.paste(tiles[ch],pos)
            else:
                score=0
                if self.map_[y-1,x]==' ':score+=1
                if self.map_[y-1,x+1]==' ':score+=2
                if self.map_[y,x+1]==' ':score+=4
                if self.map_[y+1,x+1]==' ':score+=8
                if self.map_[y+1,x]==' ':score+=16
                if self.map_[y+1,x-1]==' ':score+=32
                if self.map_[y,x-1]==' ':score+=64
                if self.map_[y-1,x-1]==' ':score+=128
                mask=masks[self._maskmap[score]]
                temp=Image.composite(wall,wall_floor,mask)
                final.paste(temp,pos)
                
        final.save(f'maps/dun_gen_fancy_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png')
        
    
if not os.path.exists(os.getcwd()+'\\maps'):
    print('Creating maps folder')
    os.makedirs(os.getcwd()+'\\maps')
from nicegui import app,ui


class Data:
    def __init__(self):
        self.rooms_width=5
        self.rooms_height=4
        self.cell_width=24
        self.cell_height=13
        self.mode=0
        self.density=0.6
        self.merge_chance=0.05
        self.search_range=1
        self.extra_walk_count=0
        self.extra_walk_length=100
        self.bonus_connections=0
        

dungeon_data=Data()

def make_dungeon_and_thumbnail():
    dungeon=Dungeon(cell_count=(dungeon_data.rooms_width,dungeon_data.rooms_height),
                    map_size=(dungeon_data.rooms_width*dungeon_data.cell_width,dungeon_data.rooms_height*dungeon_data.cell_height),
                    mode=dungeon_data.mode,density=dungeon_data.density, merge_chance=dungeon_data.merge_chance,
                    search_range=dungeon_data.search_range,extra_walk_count=dungeon_data.extra_walk_count,
                    extra_walk_length=dungeon_data.extra_walk_length,bonus_connections=dungeon_data.bonus_connections)
    thumb=dungeon.render_thumbnail()
    return dungeon,thumb


d,th=make_dungeon_and_thumbnail()
size={'s':f'Final Map Size: {d.map_width*16}x{d.map_height*16}'}
@ui.page('/')
def page():     
    with ui.row():
        with ui.column():
            v = ui.checkbox('Advanced Options', value=False)
            with ui.column().bind_visibility_from(v, 'value'):
                
                ui.number("Map Columns",value=5,min=1,max=16).bind_value(dungeon_data, 'rooms_width').props("size=10")
                ui.number("Map Rows",value=4,min=1,max=16).bind_value(dungeon_data, 'rooms_height').props("size=10")
                ui.number("Cell Width",value=24,min=12,max=40).bind_value(dungeon_data, 'cell_width').props("size=10")
                ui.number("Cell Height",value=13,min=10,max=40).bind_value(dungeon_data, 'cell_height').props("size=10")

                

                ui.number("Bonus Connections",value=0,min=0).bind_value(dungeon_data, 'bonus_connections').props("size=10")
                ui.number("Extra Paths",value=0,min=0).bind_value(dungeon_data, 'extra_walk_count').props("size=10")
                ui.number("Extra Path length",value=100,min=0).bind_value(dungeon_data, 'extra_walk_length').props("size=10")
                dc = ui.checkbox('Danger Zone', value=False)
                with ui.column().bind_visibility_from(dc, 'value'):
                    ui.label('Room density (Use caution with low values)')
                    ui.label('')
                    density_slider=ui.slider(min=0, max=1,step=.001,value=0.6).props('label-always').bind_value(dungeon_data, 'density')
                    density_slider.bind_value_to(density_slider.props, 'label-value', lambda x: f'{x*100:.1f}%')
                    ui.label('Merge Chance (Use caution with high values)')
                    ui.label('')
                    merge_slider=ui.slider(min=0, max=1,step=.001,value=0.05).props('label-always').bind_value(dungeon_data, 'merge_chance')
                    merge_slider.bind_value_to(merge_slider.props, 'label-value', lambda x: f'{x*100:.1f}%')
        img=ui.image(th).props(f"width={th.width*6}px height={th.height*6}px").style('image-rendering: pixelated;')




    def dungeon_wrapper():
        global d; global th
        d,th = make_dungeon_and_thumbnail()
        img.set_source(th)
        img.props(f"width={th.width*6}px height={th.height*6}px").style('image-rendering: pixelated;')
        size['s']=f'Final Map Size: {d.map_width*16}x{d.map_height*16}'
        
    def render_wrapper():
        d.fancy_render()
    final_render_label=ui.label().bind_text_from(size,'s')
    with ui.row():
        ui.button('Generate', on_click=dungeon_wrapper)
        ui.button('Save', on_click=render_wrapper)
        ui.button('Exit', on_click=app.shutdown)
ui.run(title='Dun_Gen UI',reload=False)
