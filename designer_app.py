from level_designer_utility import *
from workspace_setup import workspace

class Designer_App(pygame.Surface):
    def __init__(self,win,width:int,height:int):
        super().__init__((width,height))

        self.master = win
        self.rect = pygame.Rect(0,0,width,height)

        #data
        self.selected_sprite = None
        self.sprite_size = (40,40)

        #flags/events
        self.mouse_pressed = None
        self.mouse_clicked = None
        self.mouse_pos = None
        self.mouse_scroll = None
        self.key_down = None

        self.start = 3
        self.initial_mouse_pos = None
        self.prev_pos = None

        #screens
        self.creative_screen = creative_section(self,1000,self.rect.height,(0,0),self.sprite_size)
        self.tool_screen = tool_section(self,200,self.rect.height,(1000,0))

        #workspace
        self.workspace = workspace(self.sprite_size)

        pygame.mouse.set_cursor(pygame.cursors.broken_x)
        self.add_command_to_btn()

    def add_command_to_btn(self):
        self.tool_screen.buttons[0].command = self.workspace.setup_workspace
        self.tool_screen.buttons[1].command = self.workspace.export_map
        self.tool_screen.buttons[2].command = self.workspace.import_map
        self.tool_screen.buttons[3].command = self.workspace.get_sprites

    def update(self):
        self.mouse_pressed = pygame.mouse.get_pressed(3)
        self.mouse_clicked = pygame.event.get(pygame.MOUSEBUTTONDOWN)
        self.mouse_pos = pygame.mouse.get_pos()
        self.mouse_scroll = pygame.event.get(pygame.MOUSEWHEEL)
        self.key_down = pygame.event.get(pygame.KEYDOWN)
    
    def sub_tuple(self,pos:tuple[int, int],rel_to:tuple[int, int]):
        return tuple(map(lambda a,b: a-b,pos,rel_to))
    
    def add_tuple(self,pos:tuple[int, int],rel_to:tuple[int, int]):
        return tuple(map(lambda a,b: a+b,pos,rel_to))
    
    def abs_div_tuple(self,pos:tuple[int, int],rel_to:tuple[int, int]):
        return tuple(map(lambda a,b: a//b,pos,rel_to))

    def bind_values(self):
        self.tool_screen.navigation_section.sprites = self.workspace.json_template['sprite_keys']
        self.creative_screen.dict_buffer = self.workspace.json_template['map']
        self.creative_screen.sprite_path = self.workspace.sprite_dir_path
        self.creative_screen.cached_sprites = self.workspace.cached_sprites
        self.creative_screen.sprite_keys = self.workspace.json_template['sprite_keys']
        self.sprite_size = self.creative_screen.sprite_size = self.workspace.sprite_size
        self.tool_screen.preview_section.set_preview_image(None)
        self.start = 3

    def draw(self):

        self.update()

        if self.key_down:
            match self.key_down[0].unicode:
                case 'c': self.creative_screen.user_mode = 1
                case 'v': self.creative_screen.user_mode = 0
                case 's': print(self.creative_screen.dict_buffer)

        if self.creative_screen.rect.collidepoint(self.mouse_pos) or self.start:
            self.creative_screen.draw()

            if self.creative_screen.user_mode:
                if self.mouse_pressed[0] and self.selected_sprite:
                    self.creative_screen.add_to_map(self.selected_sprite, self.mouse_pos)
                elif self.mouse_pressed[2]:
                    self.creative_screen.remove_from_map(self.mouse_pos)
                
            else:
                if self.mouse_pressed[0]:
                    self.creative_screen.shift_offset.xy = self.add_tuple(self.prev_pos, self.sub_tuple(self.mouse_pos,self.initial_mouse_pos))
                else:
                    self.initial_mouse_pos = self.mouse_pos
                    self.prev_pos = self.creative_screen.shift_offset.xy

        if self.tool_screen.rect.collidepoint(self.mouse_pos) or self.start:
            self.tool_screen.draw()
            
            for btn in self.tool_screen.buttons:
                if btn.rect.collidepoint(self.sub_tuple(self.mouse_pos,self.tool_screen.rect.topleft)):
                    btn.set_alpha(100)
                    if self.mouse_clicked and self.mouse_clicked[0].button == 1:
                        if btn.command():
                            self.bind_values()
                else:
                    btn.set_alpha(80)
                btn.draw()
            
            self.tool_screen.preview_section.draw()
            self.tool_screen.navigation_section.draw()

            rel_pos = self.sub_tuple(self.mouse_pos,self.tool_screen.rect.topleft)

            if self.mouse_scroll:
                if self.tool_screen.navigation_section.rect.collidepoint(rel_pos):
                    if self.mouse_scroll[0].y > 0: self.tool_screen.navigation_section.scroll_offset_y = max(0,self.tool_screen.navigation_section.scroll_offset_y-1)
                    else: self.tool_screen.navigation_section.scroll_offset_y = min(self.workspace.json_template['sprite_keys'].__len__()-1,self.tool_screen.navigation_section.scroll_offset_y+1)
            
            elif self.mouse_clicked:
                if self.tool_screen.navigation_section.rect.collidepoint(rel_pos):
                    try:
                        self.selected_sprite = self.workspace.json_template['sprite_keys'][self.tool_screen.navigation_section.scroll_offset_y+self.sub_tuple(rel_pos,(0,self.tool_screen.navigation_section.rect.y))[1]//30]
                        self.tool_screen.preview_section.set_preview_image(self.workspace.cached_sprites[self.selected_sprite])
                    except:
                        ...

        if self.workspace.is_updated:
            self.tool_screen.draw()
            self.tool_screen.navigation_section.draw()
            self.tool_screen.preview_section.draw()
            self.creative_screen.cache_sprites()
            self.workspace.is_updated = False

        if self.start: self.start -= 1

        self.master.blit(self,(0,0))