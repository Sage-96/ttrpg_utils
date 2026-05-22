import os
from modules.dungeon import Dungeon

if not os.path.exists(os.getcwd()+'\\maps'):
    print('Creating maps folder')
    os.makedirs(os.getcwd()+'\\maps')
from nicegui import app,ui,native


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
    dungeon,thumb=dungeon.render_thumbnail()
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
    def uvtt_wrapper():
        d.make_uvtt()
    final_render_label=ui.label().bind_text_from(size,'s')
    with ui.row():
        ui.button('Generate', on_click=dungeon_wrapper)
        ui.button('Save Image', on_click=render_wrapper)
        ui.button('Save as UVTT file', on_click=uvtt_wrapper)
        ui.button('Exit', on_click=app.shutdown)
ui.run(title='Dun_Gen UI',reload=False,host='localhost',port=native.find_open_port())

