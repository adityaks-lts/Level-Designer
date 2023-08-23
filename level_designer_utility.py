import pygame
from time import time

class sprite_navigator(pygame.Surface):
    def __init__(self, master, width, height, pos:tuple[int, int]):
        super().__init__((width,height))
        self.master = master
        self.rect = self.get_rect(topleft=pos)
        self.font_kernel = pygame.font.SysFont("comicsans", 20, True)
        self.scroll_offset_y = 0
        self.draw_count = (self.rect.height-4)//30

        self.sprites = None
    
    def draw(self):
        self.fill((90,90,90))
        if self.sprites:
            for i in range(min(self.sprites.__len__(),self.draw_count)-self.scroll_offset_y):
                self.blit(self.font_kernel.render(self.sprites[self.scroll_offset_y+i],False,(60,60,60)),(4,2+30*i))
        self.master.blit(self, self.rect)


class preview(pygame.Surface):
    def __init__(self, master, width, height, pos:tuple[int, int]):
        super().__init__((width, height))
        self.master = master
        self.rect = self.get_rect(topleft=pos)

        self.preview_image_dimension = (int(width*.8), int(height*.8))
        self.preview_image = None
    
        self.convert_alpha()

    def set_preview_image(self, image):
        if image: self.preview_image = pygame.transform.scale(image,self.preview_image_dimension)
        else: self.preview_image = image

    def draw(self):
        self.fill((50,50,50))
        if self.preview_image: self.blit(self.preview_image, (int(self.rect.width*.1), int(self.rect.height*.1)))
        self.master.blit(self, self.rect)

class btn(pygame.Surface):
    def __init__(self,win,width:int=0,height:int=0,pos:tuple[int,int]|None=None,text:str|None = None,text_align:str = 'center',ipadx = 0, command = None):
        self.master = win
        self.text_surf = pygame.font.SysFont("comicsans", 20, True).render(text,True,(240,240,240))
        super().__init__((width, max(self.text_surf.get_height(), height)),pygame.SRCALPHA)
        self.text_rect = self.text_surf.get_rect(topleft=(0,0))
        self.rect = self.get_rect(topleft=pos)

        self.command = command if command else lambda:print("clicked")

        match text_align:
            case 'left':
                self.text_rect.left = self.rect.left+ipadx
            case 'right':
                self.text_rect.right = self.rect.right-ipadx
            case _: self.text_rect.centerx = self.rect.centerx

        self.set_alpha(80)
        self.convert_alpha()
    
    def draw(self):
        self.fill((150,150,150))
        self.blit(self.text_surf,self.text_rect)
        self.master.blit(self, self.rect)

class tool_section(pygame.Surface):
    def __init__(self,win,width:int,height:int,pos:tuple[int ,int]):
        super().__init__((width,height))

        self.master = win
        self.rect = self.get_rect(topleft=pos)

        self.buttons = [
            btn(self,196,30,(2,2),'NEW','left',ipadx=8),
            btn(self,196,30,(2,34),'EXPORT','left',ipadx=8),
            btn(self,196,30,(2,66),'IMPORT','left',ipadx=8),
            btn(self,196,30,(2,98),'LOAD','left',ipadx=8),
        ]

        self.navigation_section = sprite_navigator(self,196,400,(2,236))
        self.preview_section = preview(self,196,100,(2,132))

        
        for button in self.buttons: button.draw()
        self.preview_section.draw()
        self.navigation_section.draw()

    def draw(self):
        self.master.blit(self,self.rect)
        self.fill((70,70,70))

class creative_section(pygame.Surface):
    def __init__(self,win,width:int,height:int,pos:tuple[int ,int],sprite_size):
        super().__init__((width,height))

        self.master = win
        self.rect = self.get_rect(topleft=pos)
        self.shift_offset = pygame.math.Vector2(0,0)
        self.font_kernel = pygame.font.SysFont("comicsans", 14)

        self.user_mode = 1
        self.sprite_size = sprite_size
        self.sprite_count = (self.rect.w//self.sprite_size[0]+1 ,self.rect.h//self.sprite_size[1]+1)
        self.mode_dict = {
            0:"VIEW MODE",
            1:"CREATIVE MODE",
                        }

        self.sprite_path = None
        self.dict_buffer = None
        self.sprite_keys = None
        self.cached_sprites = None

    def cache_sprites(self):
        for sprite in self.sprite_keys[::-1]:
            if self.cached_sprites.get(sprite): break
            else: self.cached_sprites[sprite] = pygame.transform.scale(pygame.image.load(f'{self.sprite_path}//{sprite}').convert_alpha(),self.sprite_size)

    def add_to_map(self,sprite_key,pos):
        pos_key = pos-self.shift_offset
        pos_key = pos_key[0]//self.sprite_size[0],pos_key[1]//self.sprite_size[1]
        if self.dict_buffer.get(pos_key[1]) == None:
            self.dict_buffer[pos_key[1]] = {pos_key[0]:sprite_key}
        else:
            self.dict_buffer[pos_key[1]][pos_key[0]] = sprite_key

    def remove_from_map(self,pos):
        pos_key = pos-self.shift_offset
        pos_key = pos_key[0]//self.sprite_size[0],pos_key[1]//self.sprite_size[1]
        if row:=self.dict_buffer.get(pos_key[1]):
            if row.get(pos_key[0]): del self.dict_buffer[pos_key[1]][pos_key[0]]

    def draw(self):
        self.master.blit(self,self.rect)
        self.fill((220,220,220))

        off_x, off_y = map(lambda a,b:int(a//b), self.shift_offset.xy, self.sprite_size)

        if self.dict_buffer:
            for y in range(-1-off_y,self.sprite_count[1]-off_y):
                if row:=self.dict_buffer.get(y):
                    for x in range(-1-off_x,self.sprite_count[0]-off_x):
                        if column:=row.get(x):
                            self.blit(self.cached_sprites[column],(self.sprite_size[0]*x,self.sprite_size[1]*y)+self.shift_offset)
        
        self.blit(self.font_kernel.render(f"{self.shift_offset.xy}", True, (0,0,0)),(4,4))
        self.blit(self.font_kernel.render(f"{self.mode_dict[self.user_mode]}", True, (0,0,0)),(self.rect.centerx,4))
