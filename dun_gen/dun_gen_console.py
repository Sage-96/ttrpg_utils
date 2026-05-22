import os
from modules.dungeon import Dungeon
    
      
if __name__=='__main__':
    
    if not os.path.exists(os.getcwd()+'\\maps'):
        print('Creating maps folder')
        os.makedirs(os.getcwd()+'\\maps')
    
    d=Dungeon((5,4),mode=0,cull=[(0,0),(1,1),(1,2),(4,1)],extra_walk_count=2,debug=True,wall_char='█')
    '''d.show_cell_boundaries()'''
    '''d=Dungeon((2,2))'''
    d.show()
    d.fancy_render()
    #d.make_uvtt()

