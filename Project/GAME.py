"""
Platformer Game
"""
import arcade
import nonmain
import Enemies
import time



# Constants of the window
SCREEN_WIDTH = nonmain.SCREEN_WIDTH
SCREEN_HEIGHT = nonmain.SCREEN_HEIGHT
SCREEN_TITLE = nonmain.SCREEN_TITLE

# Constants used to scale our sprites from their original size
CHARACTER_SCALING = 1.5
TILE_SCALING = 1.5
SPRITE_PIXEL_SIZE = 16
GRID_PIXEL_SIZE = (SPRITE_PIXEL_SIZE * TILE_SCALING)

NBG=7 #Число слоёв бэк и форграунда
NFG = 3
NEN = 2 #Число врагов на уровне, не считая двигающихся ловушек
# Constants used to track if the player is facing left or right
RIGHT_FACING = 0
LEFT_FACING = 1

# Movement speed of player, in pixels per frame
PLAYER_MOVEMENT_SPEED = 7
PLAYER_LADDER_MOVEMENT_SPEED = 4
# PLAYER_START_X = 768
# PLAYER_START_Y = 1216
PLAYER_START_X = 32  # center of player
PLAYER_START_Y = 64  # bottom of the player
GRAVITY = 1
PLAYER_JUMP_SPEED = 16
DASH_BUFF = 5
DASH_DISTANCE = GRID_PIXEL_SIZE*6 #ЦИФЕРКА - КОЛВО БЛОКОВ НА ДАШ
SLIDE_DISTANCE = GRID_PIXEL_SIZE*4
DASH_COOLDOWN = 0.6
IMMUNITY_TIME = 1

# How many pixels to keep as a minimum margin between the character
# and the edge of the screen.
LEFT_VIEWPORT_MARGIN = int(SCREEN_WIDTH / 2)
RIGHT_VIEWPORT_MARGIN = int(SCREEN_WIDTH / 2)
BOTTOM_VIEWPORT_MARGIN = int(SCREEN_HEIGHT / 5)
TOP_VIEWPORT_MARGIN = int(SCREEN_HEIGHT / 5*4)

#Classes from nonmain
GameOverView = nonmain.GameOverView
PauseView = nonmain.PauseView
MenuView = nonmain.MenuView
GameWindow = nonmain.GameWindow
LevelCompletedView = nonmain.LevelCompletedView

#Список с противниками
All_enemies = [None,
               [Enemies.Skeleton_Seeker(), Enemies.Skeleton_Lighter()],
               [Enemies.Skeleton_Seeker(), Enemies.Skeleton_Lighter()] ]
#All_enemies[1000]=[Enemies.Old_Guardian(), Enemies.Skeleton_Lighter()]

def load_texture_pair(filename):
    """
    Load a texture pair, with the second being a mirror image.
    """
    return [
        arcade.load_texture(filename),
        arcade.load_texture(filename, flipped_horizontally=True)
    ]


class PlayerCharacter(arcade.Sprite):
    """ Player Sprite"""

    def __init__(self):

        # Set up parent class
        super().__init__()

        # Default to face-right
        self.character_face_direction = RIGHT_FACING

        # Used for flipping between image sequences
        self.cur_texture = 0
        self.scale = CHARACTER_SCALING

        # Track our state
        self.can_jump = False
        self.climbing = False
        self.is_on_ladder = False
        self.dashing = False
        self.dashing_end = False
        self.sliding = False
        self.sliding_end = False
        self.hurt = False
        self.dead = False
        # --- Load Textures ---

        main_path = "images/Warrior/Individual Sprite/"

        # Текстуры для стойки
        self.idle_textures = []
        for i in range(1, 7):
            texture = load_texture_pair(f"{main_path}idle/Warrior_Idle_{i}.png")
            self.idle_textures.append(texture)

        # Текстуры для прыжка
        self.jump_textures = []
        for i in range(1, 4):
            texture = load_texture_pair(f"{main_path}Jump/Warrior_Jump_{i}.png")
            self.jump_textures.append(texture)

        # Текстуры перехода в верхней точке
        self.up_to_fall_textures = []
        for i in range(1, 3):
            texture = load_texture_pair(f"{main_path}UptoFall/Warrior_UptoFall_{i}.png")
            self.up_to_fall_textures.append(texture)

        # Текстуры падения
        self.fall_textures = []
        for i in range(1, 4):
            texture = load_texture_pair(f"{main_path}Fall/Warrior_Fall_{i}.png")
            self.fall_textures.append(texture)

        # Текстуры бега
        self.run_textures = []
        for i in range(1, 9):
            texture = load_texture_pair(f"{main_path}Run/Warrior_Run_{i}.png")
            self.run_textures.append(texture)

        # Текстуры для лестницы
        self.ladder_grab_textures = []
        for i in range(1, 9):
            texture = arcade.load_texture(f"{main_path}Ladder-Grab/Warrior-Ladder-Grab_{i}.png")
            self.ladder_grab_textures.append(texture)

        # Текстуры дэша
        self.dash_textures = []
        for i in range(1, 8):
            texture = load_texture_pair(f"{main_path}Dash/Warrior_Dash_{i}.png")
            self.dash_textures.append(texture)

        # Текстуры слайда
        self.slide_textures = []
        for i in range(1, 6):
            texture = load_texture_pair(f"{main_path}Slide/Warrior-Slide_{i}.png")
            self.slide_textures.append(texture)

        # Текстуры получения урона
        self.hurt_textures = []
        for i in range(1, 5):
            texture = load_texture_pair(f"{main_path}Hurt-Effect/Warrior_hurt_{i}.png")
            self.hurt_textures.append(texture)

        # Текстуры смерти
        self.death_textures = []
        for i in range(1, 12):
            texture = load_texture_pair(f"{main_path}Death-Effect/Warrior_Death_{i}.png")
            self.death_textures.append(texture)

        # Set the initial texture
        self.texture = self.idle_textures[0][0]

        # Hit box will be set based on the first image used
        self.set_hit_box(self.texture.hit_box_points)

    def update_animation(self, delta_time: float = 1 / 60):

        # Figure out if we need to flip face left or right
        if self.change_x < 0 and self.character_face_direction == RIGHT_FACING:
            self.character_face_direction = LEFT_FACING
            self.set_hit_box(self.idle_textures[0][1].hit_box_points)
        elif self.change_x > 0 and self.character_face_direction == LEFT_FACING:
            self.character_face_direction = RIGHT_FACING
            self.set_hit_box(self.idle_textures[0][0].hit_box_points)

        # Смэрть
        if self.dead:
            self.cur_texture += 1
            if self.cur_texture > 32:
                self.dead = False
                return
            self.texture = self.death_textures[self.cur_texture // 3][self.character_face_direction]
            return

        # Получение урона
        if self.hurt:
            self.cur_texture += 1
            if self.cur_texture > 19:
                self.hurt = False
                return
            self.texture = self.hurt_textures[self.cur_texture // 5][self.character_face_direction]
            return

        # Анимация на лестнице
        if self.is_on_ladder:
            self.climbing = True
        else:
            self.climbing = False
        if self.climbing:
            if (abs(self.change_y) > 0 or abs(self.change_x) > 0):
                self.cur_texture += 1
                if self.cur_texture > 63:
                    self.cur_texture = 0
                self.texture = self.ladder_grab_textures[self.cur_texture // 8]
                return


        # Dash animation. перед падением, чтобы срабатывать раньше
        if self.dashing:
            self.cur_texture += 1
            if self.cur_texture > 11:
                self.cur_texture = 0
            self.texture = self.dash_textures[self.cur_texture // 3][self.character_face_direction]
            return

        # Slide animation
        if self.sliding:
            self.texture = self.slide_textures[0][self.character_face_direction]
            self.set_hit_box(self.texture.hit_box_points)
            return

        # Jumping animation
        if self.change_y > 0 and not self.is_on_ladder:
            self.cur_texture += 1
            if self.cur_texture > 20:
                self.cur_texture = 0
            self.texture = self.jump_textures[self.cur_texture // 7][self.character_face_direction]
            return
        elif self.change_y < 0 and not self.is_on_ladder:
            self.cur_texture += 1
            if self.cur_texture > 20:
                self.cur_texture = 0
            self.texture = self.fall_textures[self.cur_texture // 7][self.character_face_direction]
            return
        elif self.change_y == 0 and not self.can_jump and not self.is_on_ladder:
            self.cur_texture += 1
            if self.cur_texture > 9:
                self.cur_texture = 0
            self.texture = self.up_to_fall_textures[self.cur_texture // 5][self.character_face_direction]
            return

        # Окончание дэша
        # Должно быть перед Idle и бегом, чтобы срабатывать раньше
        if self.dashing_end:
            self.cur_texture += 1
            if self.cur_texture > 17:
                self.cur_texture = 0
                self.dashing_end = False
                return
            self.texture = self.dash_textures[4 + self.cur_texture // 6][self.character_face_direction]
            return

        # Окончание слайда
        # Должно быть перед Idle и бегом, чтобы срабатывать раньше
        if self.sliding_end:
            self.cur_texture += 1
            if self.cur_texture > 23:
                self.cur_texture = 0
                self.sliding_end = False
                self.set_hit_box(self.idle_textures[0][self.character_face_direction].hit_box_points)
                return
            self.texture = self.slide_textures[1 + self.cur_texture // 6][self.character_face_direction]
            return


        # Idle animation
        if self.change_x == 0 and self.can_jump:
            self.cur_texture += 1
            if self.cur_texture > 41:
                self.cur_texture = 0
            self.texture = self.idle_textures[self.cur_texture // 7][self.character_face_direction]
            return

        # Анимация бега
        if abs(self.change_x) > 0 and self.can_jump and not self.dashing and not self.sliding:
            self.cur_texture += 1
            if self.cur_texture > 31:
                self.cur_texture = 0
            self.texture = self.run_textures[self.cur_texture // 4][self.character_face_direction]
            return

class GameView(arcade.View):
    """
    Main application class.
    """

    def __init__(self):

        super().__init__()
        # These are 'lists' that keep track of our sprites. Each sprite should
        # go into a list.
        self.golden_door_list = None
        self.golden_key_list = None
        self.exit_list = None
        self.coin_list = None
        self.heart_list = None
        self.wall_list = None
        self.player_list = None
        self.background=[]
        for i in range(NBG):
            list = None
            self.background.append(list)
        self.foreground=[]
        for i in range(NFG):
            list = None
            self.foreground.append(list)
        self.dont_touch_list = None
        self.ladder_list = None
        self.enemy_list = None
        self.checkpoint_list = None
        self.spawn_list = None

        # Separate variable that holds the player sprite
        self.player_sprite = None
        self.player_face_right = True
        self.player_face_right = False

        #self.timing_of_death = time.time()

        #Dash info
        self.dash_start = 0
        self.dash_start_time = 0

        # Slide info
        self.slide_start = 0
        self.slide_start_time = 0

        # Our physics engine
        self.physics_engine = None

        # Track the current state of what key is pressed
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False
        self.jump_needs_reset = False
        self.dash_pressed = False
        self.dash_is_ready =True

        # Used to keep track of our scrolling
        self.view_bottom = 0
        self.view_left = 0

        # Keep track of the score AND LIFES
        self.score = 0
        self.max_lifes=3
        self.lifes = self.max_lifes

        # Level
        self.level = 1

        # Load sounds
        self.collect_coin_sound = arcade.load_sound("sounds/coin2.wav")
        self.jump_sound = arcade.load_sound("sounds/jump2.wav")
        self.game_over_sound = arcade.load_sound("sounds/gameover1.wav")
        self.dash_sound = arcade.load_sound("sounds/dash_1.mp3")
        self.death_sound = arcade.load_sound("sounds/death_1.mp3")
        self.error_sound = arcade.load_sound("sounds/error2.wav")
        self.door_sound = arcade.load_sound("sounds/door_1.wav")
        self.key_sound = arcade.load_sound("sounds/key_1.mp3")
        self.level_completed_sound = arcade.load_sound("sounds/level_completed_1.wav")
        self.teleport_sound =  arcade.load_sound("sounds/upgrade1.wav")
        self.checkpoint_sound = arcade.load_sound("sounds/checkpoint_1.wav")
        # keys and doors
        self.has_golden_key = False
        # arcade.set_background_color(arcade.csscolor.CORNFLOWER_BLUE)

    def setup(self, level=0):
        """ Set up the game here. Call this function to restart the game. """
        # Used to keep track of our scrolling
        self.view_bottom = 0
        self.view_left = 0



        # Track the current state of what key is pressed
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False
        self.jump_needs_reset = False
        self.dash_pressed = False
        self.dash_is_ready = True

        # Keep track of the score
        self.score = 0

        # Create the Sprite lists
        self.golden_door_list = arcade.SpriteList(use_spatial_hash=True)
        self.golden_key_list = arcade.SpriteList(use_spatial_hash=True)
        self.exit_list = arcade.SpriteList(use_spatial_hash=True)
        self.checkpoint_list = arcade.SpriteList(use_spatial_hash=True)
        self.enemy_list = arcade.SpriteList()
        self.player_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList(use_spatial_hash=True)
        self.coin_list = arcade.SpriteList(use_spatial_hash=True)
        self.heart_list = arcade.SpriteList(use_spatial_hash=True)
        for i in range(NBG):
            self.background[i] = arcade.SpriteList()
        for i in range(NFG):
            self.foreground[i] = arcade.SpriteList()
        self.spawn_list = arcade.SpriteList()


        # Dash info
        self.dash_start = 0
        self.dash_start_time = 0

        # Slide info
        self.slide_start = 0
        self.slide_start_time = 0

        #Knockback
        self.time_of_being_hurted = 0

        # --- Load in a map from the tiled editor ---

        # Map name
        map_name = f"maps/map_level_{level}.tmx"
        
            
        # Read in the tiled map
        try:
            my_map = arcade.tilemap.read_tmx(map_name)
        except:
            self.window.show_view(MenuView())
            return

        # # -- Background

        for i in range(NBG):
            self.background[i] =arcade.tilemap.process_layer(my_map, f"Background {NBG-i}", TILE_SCALING)

        # exit
        self.exit_list = arcade.tilemap.process_layer(my_map,
                                                      'Exit',
                                                      TILE_SCALING)

        #Enemies
        #Враги как движущиеся ловушки
        self.enemy_list=arcade.tilemap.process_layer(my_map,
                                                              'Enemies',
                                                              TILE_SCALING)
        # Нормальные враги
        for i in range(NEN):
            temporary_enemy_list = arcade.tilemap.process_layer(my_map,
                                                              f"Enemy {i}", TILE_SCALING)

            for enemy in temporary_enemy_list:
                this_enemy = All_enemies[self.level][i]
                this_enemy.center_x = enemy.center_x
                this_enemy.bottom = enemy.bottom
                self.enemy_list.append(this_enemy)

        # -- Ladder objects
        self.ladder_list = arcade.tilemap.process_layer(my_map,
                                                        'Ladders',
                                                        scaling=TILE_SCALING,
                                                        use_spatial_hash=True)

        # -- Foreground
        for i in range(NFG):
            self.foreground[i] = arcade.tilemap.process_layer(my_map, f"Foreground {NFG - i}", TILE_SCALING)

        # -- Platforms
        self.wall_list = arcade.tilemap.process_layer(map_object=my_map,
                                                      layer_name='Platforms',
                                                      scaling=TILE_SCALING,
                                                      use_spatial_hash=True)
        # -- Moving Platforms
        moving_platforms_list = arcade.tilemap.process_layer(my_map, 'Moving platforms', TILE_SCALING)
        for sprite in moving_platforms_list:
            self.wall_list.append(sprite)
        # checkpoints
        self.checkpoint_list = arcade.tilemap.process_layer(my_map, 'Checkpoints', TILE_SCALING,
                                                            use_spatial_hash=True)


        # -- Coins
        self.coin_list = arcade.tilemap.process_layer(my_map,
                                                      'Coins',
                                                      TILE_SCALING,
                                                      use_spatial_hash=True)
        # -- Hearts
        self.heart_list = arcade.tilemap.process_layer(my_map,
                                                      'Hearts',
                                                      TILE_SCALING,
                                                      use_spatial_hash=True)

        # -- Don't Touch Layer
        self.dont_touch_list = arcade.tilemap.process_layer(my_map,
                                                            "Don't Touch",
                                                            TILE_SCALING,
                                                            use_spatial_hash=True)

        # doors and keys
        self.golden_key_list = arcade.tilemap.process_layer(my_map,
                                                            'Golden key',
                                                            TILE_SCALING,
                                                            use_spatial_hash=True)
        self.golden_door_list = arcade.tilemap.process_layer(my_map,
                                                             'Golden door',
                                                             TILE_SCALING,
                                                             use_spatial_hash=True)

        #Спавн
        self.spawn_list=arcade.tilemap.process_layer(my_map,
                                                      'Spawn',
                                                      TILE_SCALING)

        # --- Other stuff
        #Края карты
        self.map_top = (my_map.map_size.height) * GRID_PIXEL_SIZE
        self.map_right = (my_map.map_size.width) * GRID_PIXEL_SIZE
        self.map_left = 0
        self.map_bottom = 0
        # Set the background color
        if my_map.background_color:
            arcade.set_background_color(my_map.background_color)
            self.background_color = my_map.background_color
        else:
            self.background_color = arcade.csscolor.PURPLE

        # checkpoint data
        self.current_checkpoint = None
        self.checkpoint_x = self.spawn_list[0].center_x
        self.checkpoint_y =self.spawn_list[0].bottom

        # Set up the player, specifically placing it at spawn
        self.player_sprite = PlayerCharacter()
        self.player_sprite.center_x = self.spawn_list[0].center_x
        self.player_sprite.bottom = self.spawn_list[0].bottom
        self.player_list.append(self.player_sprite)

        # Create the 'physics engine'
        self.physics_engine = arcade.PhysicsEnginePlatformer(self.player_sprite,
                                                             self.wall_list,
                                                             gravity_constant=GRAVITY,
                                                             ladders=self.ladder_list)

    def on_draw(self):
        """ Render the screen. """

        # Clear the screen to the background color
        arcade.start_render()

        # Draw our sprites
        for i in self.background:
            i.draw()
        self.checkpoint_list.draw()
        self.wall_list.draw()
        self.golden_key_list.draw()
        self.golden_door_list.draw()
        self.coin_list.draw()
        self.heart_list.draw()
        self.dont_touch_list.draw()
        self.enemy_list.draw()
        self.exit_list.draw()
        self.ladder_list.draw()
        self.player_list.draw()
        for i in self.foreground:
            i.draw()

        # Draw our score on the screen, scrolling it with the viewport

        score_text = f"Score: {self.score}"
        arcade.draw_text(score_text, 20 + self.view_left, SCREEN_HEIGHT - 30 + self.view_bottom,
                         arcade.csscolor.BLACK, 18)
        arcade.draw_text(f'Level {self.level}', 20 + self.view_left, SCREEN_HEIGHT - 50 + self.view_bottom,
                         arcade.csscolor.BLACK, 18)
        #player_name
        #arcade.draw_text('Pasha +PLUS+', self.player_sprite.left - 32, self.player_sprite.top, arcade.csscolor.WHITE, 18)
        arcade.draw_text(f"Lifes: {self.lifes}", 20 + self.view_left, SCREEN_HEIGHT - 70 + self.view_bottom,
                         arcade.csscolor.BLACK, 18)
        #keys
        if self.has_golden_key:
            arcade.draw_text('Золотой ключ', 20 + self.view_left, SCREEN_HEIGHT - 90 + self.view_bottom,
                             arcade.csscolor.BLACK, 18)
        #dash_cooldown
        if time.time() - self.dash_start_time >= DASH_COOLDOWN:
            arcade.draw_text('Dash: ready', 130 + self.view_left, SCREEN_HEIGHT - 30 + self.view_bottom,
                             arcade.csscolor.BLACK, 18)
        else:
            arcade.draw_text(f"Dash: {round(DASH_COOLDOWN-time.time() + self.dash_start_time)}", 130 + self.view_left, SCREEN_HEIGHT - 30 + self.view_bottom,
                             arcade.csscolor.BLACK, 18)

    def process_keychange(self):
        """
        Called when we change a key up/down or we move on/off a ladder.
        """
        # Process up/down
        if self.up_pressed and not self.down_pressed:
            if self.physics_engine.is_on_ladder():
                self.player_sprite.change_y = PLAYER_LADDER_MOVEMENT_SPEED
            elif self.physics_engine.can_jump() and not self.jump_needs_reset:
                self.player_sprite.change_y = PLAYER_JUMP_SPEED
                self.jump_needs_reset = True
                arcade.play_sound(self.jump_sound)
        elif self.down_pressed and not self.up_pressed:
            if self.physics_engine.is_on_ladder():
                self.player_sprite.change_y = -PLAYER_LADDER_MOVEMENT_SPEED


        # Process up/down when on a ladder and no movement
        if self.physics_engine.is_on_ladder():
            if not self.up_pressed and not self.down_pressed:
                self.player_sprite.change_y = 0
            elif self.up_pressed and self.down_pressed:
                self.player_sprite.change_y = 0

        # Process left/right
        if self.dash_pressed:
            self.player_sprite.dashing = True
            self.player_sprite.change_y = 0
            if self.player_sprite.character_face_direction == RIGHT_FACING:
                self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED * DASH_BUFF
            elif self.player_sprite.character_face_direction == LEFT_FACING:
                self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED * DASH_BUFF
        elif self.left_pressed and not self.right_pressed and not self.player_sprite.sliding_end:
            if self.down_pressed and not self.player_sprite.sliding and self.physics_engine.can_jump():
                self.slide_start_time = time.time()
                self.slide_start = self.player_sprite.center_x
                self.player_sprite.sliding = True
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
        elif self.right_pressed and not self.left_pressed and not self.player_sprite.sliding_end:
            if self.down_pressed and not self.player_sprite.sliding and self.physics_engine.can_jump():
                self.slide_start_time = time.time()
                self.slide_start = self.player_sprite.center_x
                self.player_sprite.sliding = True
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED
        else:
            self.player_sprite.change_x = 0

    def key_discard(self):#просто функция для сброса любого движения
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False
        self.jump_needs_reset = False
        self.dash_pressed = False
        self.player_sprite.change_y = 0
        self.process_keychange()

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed. """

        if key == arcade.key.W or key == arcade.key.SPACE:
            self.up_pressed = True
        elif key == arcade.key.S:
            self.down_pressed = True
        elif key == arcade.key.A:
            self.left_pressed = True
        elif key == arcade.key.D:
            self.right_pressed = True
        if (key == arcade.key.LSHIFT) and (time.time() - self.dash_start_time >= DASH_COOLDOWN) and (not self.player_sprite.sliding
                or self.player_sprite.sliding_end):
            arcade.play_sound(self.dash_sound)
            self.dash_start_time = time.time()
            self.dash_pressed = True
            self.dash_start = self.player_sprite.center_x

        self.process_keychange()

        if key == arcade.key.ESCAPE:
            gpause = PauseView(self, self.background_color)
            self.window.show_view(gpause)
        # if key == arcade.key.F:
        # User hits f. Flip between full and not full screen.
        #    self.window.set_fullscreen(not self.window.fullscreen)

        # Get the window coordinates. Match viewport to window coordinates
        # so there is a one-to-one mapping.
        #    width, height = self.window.get_size()
        #    arcade.set_viewport(0, width, 0, height)

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key. """

        if key == arcade.key.W or key == arcade.key.SPACE:
            if self.player_sprite.change_y>0:
                self.player_sprite.change_y = 0
            self.jump_needs_reset = False
            self.up_pressed = False
        elif key == arcade.key.S:
            self.down_pressed = False
        elif key == arcade.key.A:
            self.left_pressed = False
        elif key == arcade.key.D:
            self.right_pressed = False

        self.process_keychange()

    def on_update(self, delta_time):
        def death():
            self.player_sprite.dead = True
            self.player_sprite.cur_texture = 0
            arcade.play_sound(self.death_sound)
            self.player_sprite.center_x = self.checkpoint_x
            self.player_sprite.bottom = self.checkpoint_y
            self.lifes = self.max_lifes
            self.key_discard()

            # Set the camera to the start
            self.view_left = 0
            self.view_bottom = 0
            # over_view = GameOverView(self, self.background_color)
            # self.window.show_view(over_view)
        def hurt(enemy):
            if self.lifes>1:
                self.player_sprite.hurt = True
                self.player_sprite.cur_texture = 0
                self.lifes -= 1
                self.time_of_being_hurted=time.time()
                if self.player_sprite.center_x - enemy.center_x>0:
                    self.player_sprite.character_face_direction = LEFT_FACING
                    #self.player_sprite.center_x += GRID_PIXEL_SIZE
                elif self.player_sprite.center_x - enemy.center_x<0:
                    self.player_sprite.character_face_direction = RIGHT_FACING
                    #self.player_sprite.center_x -= GRID_PIXEL_SIZE
                # if self.player_sprite.center_y - enemy.center_y>0:
                #     self.player_sprite.center_y += GRID_PIXEL_SIZE
                # elif self.player_sprite.center_y - enemy.center_y<0:
                #     self.player_sprite.center_y -= GRID_PIXEL_SIZE

            else:
                death()



        """ Movement and game logic """
        # Dashing
        if (abs(self.player_sprite.center_x - self.dash_start)> DASH_DISTANCE
            or (time.time() - self.dash_start_time > DASH_DISTANCE/(60*PLAYER_MOVEMENT_SPEED * DASH_BUFF)))\
                and self.dash_pressed:
            if self.physics_engine.can_jump():
                self.player_sprite.dashing_end = True
                self.player_sprite.cur_texture = 0
            self.dash_pressed = False
            self.process_keychange()

        # Sliding
        if (abs(self.player_sprite.center_x - self.slide_start)> SLIDE_DISTANCE
            or (time.time() - self.slide_start_time > SLIDE_DISTANCE/(60*PLAYER_MOVEMENT_SPEED)))\
                and self.player_sprite.sliding:
            self.player_sprite.cur_texture = 0
            self.player_sprite.sliding_end = True
            self.player_sprite.sliding = False
            self.process_keychange()


        #Уперся ли персонаж в край карты?
        if self.player_sprite.left<self.map_left:
            self.player_sprite.left = self.map_left
        elif self.player_sprite.right>self.map_right:
            self.player_sprite.right = self.map_right
        elif self.player_sprite.top>self.map_top:
            self.player_sprite.top = self.map_top
        # elif self.player_sprite.bottom<self.map_bottom:
        #     self.player_sprite.bottom=self.map_bottom
        # Move the player with the physics engine
        self.physics_engine.update()

        # Update animations
        if self.physics_engine.can_jump():
            self.player_sprite.can_jump = True
        else:
            self.player_sprite.can_jump = False

        if self.physics_engine.is_on_ladder() and not self.physics_engine.can_jump():
            self.player_sprite.is_on_ladder = True
            self.process_keychange()
        else:
            self.player_sprite.is_on_ladder = False
            self.process_keychange()

        if self.dash_pressed:
            self.player_sprite.dashing = True
        else:
            self.player_sprite.dashing = False

        self.background[NBG-1].update_animation(delta_time)
        #self.background[NBG - 2].update_animation(delta_time)
        self.foreground[NFG - 1].update_animation(delta_time)
        self.coin_list.update_animation(delta_time)
        self.dont_touch_list.update_animation(delta_time)
        self.heart_list.update_animation(delta_time)
        self.enemy_list.update_animation(delta_time)
        self.player_list.update_animation(delta_time)


        # Update walls, used with moving platforms
        self.wall_list.update()
        # update enemies
        self.enemy_list.update()

        # Check each enemy trap
        for enemy in self.enemy_list:
            # If the enemy hits a wall, reverse
            for wall in arcade.check_for_collision_with_list(enemy, self.wall_list):
                if wall.collides_with_point([enemy.right,enemy.center_y]) and enemy.change_x > 0:
                    enemy.change_x *= -1
                elif wall.collides_with_point([enemy.left,enemy.center_y]) and enemy.change_x < 0:
                    enemy.change_x *= -1
                elif wall.collides_with_point([enemy.center_x,enemy.top]) and enemy.change_y > 0:
                    enemy.change_y *= -1
                elif wall.collides_with_point([enemy.center_x,enemy.bottom]) and enemy.change_y < 0:
                    enemy.change_y *= -1
            # If the enemy hit the left boundary, reverse
            if enemy.boundary_left and enemy.left < enemy.boundary_left and enemy.change_x < 0:
                enemy.change_x *= -1
            # If the trap hit the right boundary, reverse
            elif enemy.boundary_right and enemy.right > enemy.boundary_right and enemy.change_x > 0:
                enemy.change_x *= -1
            elif enemy.boundary_top and enemy.top > enemy.boundary_top and enemy.change_y > 0:
                enemy.change_y *= -1
            elif enemy.boundary_bottom and enemy.bottom < enemy.boundary_bottom and enemy.change_y < 0:
                enemy.change_y *= -1



        # See if the wall hit a boundary and needs to reverse direction.
        for wall in self.wall_list:
            if wall.boundary_right and wall.right > wall.boundary_right and wall.change_x > 0:
                wall.change_x *= -1
            if wall.boundary_left and wall.left < wall.boundary_left and wall.change_x < 0:
                wall.change_x *= -1
            if wall.boundary_top and wall.top > wall.boundary_top and wall.change_y > 0:
                wall.change_y *= -1
            if wall.boundary_bottom and wall.bottom < wall.boundary_bottom and wall.change_y < 0:
                wall.change_y *= -1

        # See if we hit any coins
        # Loop through each coin we hit (if any) and remove it
        for coin in arcade.check_for_collision_with_list(self.player_sprite,
                                                             self.coin_list):
            # Remove the coin
            coin.remove_from_sprite_lists()
            # Play a sound
            arcade.play_sound(self.collect_coin_sound)
            # Add one to the score
            self.score += 10

        # See if we hit any hearts
        # Loop through each heart we hit (if any) and remove it
        for heart in arcade.check_for_collision_with_list(self.player_sprite,
                                                             self.heart_list):
            # Remove the heart
            heart.remove_from_sprite_lists()
            # Play a sound
            arcade.play_sound(self.collect_coin_sound)
            # Add one to the score
            self.lifes += 1
        # checkpoints
        for save in arcade.check_for_collision_with_list(self.player_sprite,
                                                         self.checkpoint_list):
            if self.current_checkpoint != save:
                arcade.play_sound(self.checkpoint_sound)
                self.current_checkpoint = save
                self.checkpoint_x = save.center_x
                self.checkpoint_y = save.bottom

        # See if we hit any keys
        # Loop through each key we hit (if any) and remove it
        for key in arcade.check_for_collision_with_list(self.player_sprite,
                                                        self.golden_key_list):
            # Remove the key
            key.remove_from_sprite_lists()
            # Play a sound
            arcade.play_sound(self.key_sound)
            # Add one to the score
            self.has_golden_key = True
        # check door
        for door in arcade.check_for_collision_with_list(self.player_sprite,
                                                         self.golden_door_list):
            if self.has_golden_key:
                arcade.play_sound(self.door_sound)
                self.has_golden_key = False
                # Remove the door
                door.remove_from_sprite_lists()
            else:
                if self.player_sprite.change_x<0 and self.player_sprite.left < door.right:
                    self.player_sprite.left=door.right
                    arcade.play_sound(self.error_sound)
                elif self.player_sprite.change_x>0 and self.player_sprite.right > door.left:
                    self.player_sprite.right=door.left
                    arcade.play_sound(self.error_sound)
                # if self.player_sprite.change_y<0 and self.player_sprite.bottom < door.top:
                #     self.player_sprite.bottom=door.top
                # elif self.player_sprite.change_y>0 and self.player_sprite.top > door.bottom:
                #     self.player_sprite.top=door.bottom
                self.key_discard()
        # Track if we need to change the viewport
        changed_viewport = False

        if time.time()-self.time_of_being_hurted>IMMUNITY_TIME:
            # See if the player hit an enemy.
            if arcade.check_for_collision_with_list(self.player_sprite, self.enemy_list):
                hurt(arcade.check_for_collision_with_list(self.player_sprite, self.enemy_list)[0])


            # Did the player touch something they should not?
            if arcade.check_for_collision_with_list(self.player_sprite,
                                                    self.dont_touch_list):
                hurt(arcade.check_for_collision_with_list(self.player_sprite, self.dont_touch_list)[0])

        # Did the player fall off the map?
        if self.player_sprite.center_y < -100:
            death()

        # See if the user got to the end of the level
        if arcade.check_for_collision_with_list(self.player_sprite,
                                                self.exit_list):
            #play sound
            arcade.play_sound(self.level_completed_sound)

            # Advance to the next level
            # Load the next level
            self.window.show_view(LevelCompletedView(self, self.background_color))
            self.level += 1

            # Load the next level
            self.window.show_view(LevelCompletedView(self, self.background_color))

            # Set the camera to the start
            self.view_left = 0
            self.view_bottom = 0
            changed_viewport = True

        # --- Manage Scrolling ---

        # Scroll left
        left_boundary = self.view_left + LEFT_VIEWPORT_MARGIN
        if self.player_sprite.left < left_boundary and self.view_left>self.map_left :
            self.view_left -= left_boundary - self.player_sprite.left
            changed_viewport = True
        elif self.view_left < self.map_left:
            self.view_left = self.map_left

        # Scroll right
        right_boundary = self.view_left + SCREEN_WIDTH - RIGHT_VIEWPORT_MARGIN
        if self.player_sprite.right > right_boundary and self.view_left + SCREEN_WIDTH < self.map_right:
            self.view_left += self.player_sprite.right - right_boundary
            changed_viewport = True
        elif self.view_left + SCREEN_WIDTH > self.map_right:
            self.view_left = self.map_right - SCREEN_WIDTH

        # Scroll up
        top_boundary = self.view_bottom + SCREEN_HEIGHT - TOP_VIEWPORT_MARGIN
        if self.player_sprite.top > top_boundary and self.view_bottom + SCREEN_HEIGHT < self.map_top:
            self.view_bottom += self.player_sprite.top - top_boundary
            changed_viewport = True
        elif self.view_bottom + SCREEN_HEIGHT > self.map_top:
            self.view_bottom = self.map_top - SCREEN_HEIGHT

        # Scroll down
        bottom_boundary = self.view_bottom + BOTTOM_VIEWPORT_MARGIN
        if self.player_sprite.bottom < bottom_boundary and self.view_bottom > self.map_bottom:
            self.view_bottom -= bottom_boundary - self.player_sprite.bottom
            changed_viewport = True
        elif self.view_bottom < self.map_bottom:
            self.view_bottom = self.map_bottom

        if changed_viewport:
            # Only scroll to integers. Otherwise we end up with pixels that
            # don't line up on the screen
            self.view_bottom = int(self.view_bottom)
            self.view_left = int(self.view_left)

            # Do the scrolling
            arcade.set_viewport(self.view_left,
                                SCREEN_WIDTH + self.view_left,
                                self.view_bottom,
                                SCREEN_HEIGHT + self.view_bottom)


def main():
    """ Main method """
    window = GameWindow()
    # game = GameView()
    view = MenuView()
    # game.setup(game.level)
    window.show_view(view)
    arcade.run()


if __name__ == "__main__":
    main()