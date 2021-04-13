"""
Platformer Game
"""
import arcade
import nonmain
import time


# Constants of the window
SCREEN_WIDTH = nonmain.SCREEN_WIDTH
SCREEN_HEIGHT = nonmain.SCREEN_HEIGHT
SCREEN_TITLE = nonmain.SCREEN_TITLE

# Constants used to scale our sprites from their original size
CHARACTER_SCALING = 0.9
TILE_SCALING = 0.5
COIN_SCALING = 0.5
SPRITE_PIXEL_SIZE = 128
GRID_PIXEL_SIZE = (SPRITE_PIXEL_SIZE * TILE_SCALING)

# Movement speed of player, in pixels per frame
PLAYER_MOVEMENT_SPEED = 10
# PLAYER_START_X = 768
# PLAYER_START_Y = 1216
PLAYER_START_X = 32  # center of player
PLAYER_START_Y = 64  # bottom of the player
GRAVITY = 1
PLAYER_JUMP_SPEED = 20
IMMUNITY_TIME = 0.1

# How many pixels to keep as a minimum margin between the character
# and the edge of the screen.
LEFT_VIEWPORT_MARGIN = int(SCREEN_WIDTH / 2)
RIGHT_VIEWPORT_MARGIN = int(SCREEN_WIDTH / 2)
BOTTOM_VIEWPORT_MARGIN = int(SCREEN_HEIGHT / 2)
TOP_VIEWPORT_MARGIN = int(SCREEN_HEIGHT / 2)

#Classes from nonmain
GameOverView = nonmain.MenuView
PauseView = nonmain.PauseView
MenuView = nonmain.MenuView
GameWindow = nonmain.GameWindow


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
        self.wall_list = None
        self.player_list = None
        self.foreground_list = None
        self.background_list = None
        self.dont_touch_list = None
        self.ladder_list = None
        self.moving_traps_list = None
        self.enemy_list = None
        self.checkpoint_list = None

        # Separate variable that holds the player sprite
        self.player_sprite = None
        self.timing_of_death = time.time()

        # Our physics engine
        self.physics_engine = None

        # Track the current state of what key is pressed
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False
        self.jump_needs_reset = False

        # Used to keep track of our scrolling
        self.view_bottom = 0
        self.view_left = 0

        # Keep track of the score
        self.score = 0
        self.max_lifes=3
        self.lifes = self.max_lifes

        # Level
        self.level = 0

        # Load sounds
        self.collect_coin_sound = arcade.load_sound("sounds/coin2.wav")
        self.jump_sound = arcade.load_sound("sounds/jump2.wav")
        self.game_over_sound = arcade.load_sound("sounds/gameover1.wav")

        # keys and doors
        self.has_golden_key = False
        # arcade.set_background_color(arcade.csscolor.CORNFLOWER_BLUE)

    def setup(self, level=0):
        """ Set up the game here. Call this function to restart the game. """
        # Used to keep track of our scrolling
        self.view_bottom = 0
        self.view_left = 0

        # checkpoint data
        self.current_checkpoint = None
        self.checkpoint_x = PLAYER_START_X
        self.checkpoint_y = PLAYER_START_Y
        self.not_immune = True

        # Keep track of the score
        self.score = 0
        self.max_lifes=3
        self.lifes = self.max_lifes

        # Create the Sprite lists
        self.golden_door_list = arcade.SpriteList(use_spatial_hash=True)
        self.golden_key_list = arcade.SpriteList(use_spatial_hash=True)
        self.exit_list = arcade.SpriteList(use_spatial_hash=True)
        self.checkpoint_list = arcade.SpriteList(use_spatial_hash=True)
        self.moving_traps_list = arcade.SpriteList()
        self.enemy_list = arcade.SpriteList()
        self.player_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList(use_spatial_hash=True)
        self.coin_list = arcade.SpriteList(use_spatial_hash=True)
        self.foreground_list = arcade.SpriteList()
        self.background_list = arcade.SpriteList()

        # Set up the player, specifically placing it at these coordinates.
        image_source = "images/player_2/player_stand.png"
        self.player_sprite = arcade.Sprite(image_source, CHARACTER_SCALING)
        self.player_sprite.center_x = PLAYER_START_X
        self.player_sprite.center_y = PLAYER_START_Y
        self.player_list.append(self.player_sprite)
        self.timing_of_death = time.time()

        # --- Load in a map from the tiled editor ---

        # Name of the layer in the file that has our platforms/walls
        platforms_layer_name = 'Platforms'
        moving_platforms_layer_name = 'Moving platforms'
        ladders_layer_name = 'Ladders'
        # Name of the layer that has items for pick-up
        coins_layer_name = 'Coins'
        # Name of the layer that has items for foreground
        foreground_layer_name = 'Foreground'
        # Name of the layer that has items for background
        background_layer_name = 'Background'
        # Name of the layer that has items we shouldn't touch
        dont_touch_layer_name = "Don't Touch"
        # moving_traps
        moving_traps_layer_name = 'Moving traps'

        #Enemies
        enemy_layer_name = 'Enemies'

        # checkpoints
        checkpoints_layer_name = 'Checkpoints'
        # exit
        exit_layer_name = 'Exit'
        # keys and doors
        golden_key_layer_name = 'Golden key'
        golden_door_layer_name = 'Golden door'
        # Map name
        map_name = f"maps/map_level_{level}.tmx"
        
            
        # Read in the tiled map
        try:
            my_map = arcade.tilemap.read_tmx(map_name)
        except:
            self.window.show_view(MenuView())
            return
        # -- Background
        self.background_list = arcade.tilemap.process_layer(my_map,
                                                            background_layer_name,
                                                            TILE_SCALING)
        # exit
        self.exit_list = arcade.tilemap.process_layer(my_map,
                                                      exit_layer_name,
                                                      TILE_SCALING)
        for sprite in self.exit_list:
            self.background_list.append(sprite)
        # moving_traps
        self.moving_traps_list = arcade.tilemap.process_layer(my_map,
                                                              moving_traps_layer_name,
                                                              TILE_SCALING)
        #Enemies
        self.enemy_list = arcade.tilemap.process_layer(my_map,
                                                              enemy_layer_name,
                                                              TILE_SCALING)

        # -- Ladder objects
        self.ladder_list = arcade.tilemap.process_layer(my_map,
                                                        ladders_layer_name,
                                                        scaling=TILE_SCALING,
                                                        use_spatial_hash=True)

        # -- Foreground
        self.foreground_list = arcade.tilemap.process_layer(my_map,
                                                            foreground_layer_name,
                                                            TILE_SCALING)

        # -- Platforms
        self.wall_list = arcade.tilemap.process_layer(map_object=my_map,
                                                      layer_name=platforms_layer_name,
                                                      scaling=TILE_SCALING,
                                                      use_spatial_hash=True)
        # -- Moving Platforms
        moving_platforms_list = arcade.tilemap.process_layer(my_map, moving_platforms_layer_name, TILE_SCALING)
        for sprite in moving_platforms_list:
            self.wall_list.append(sprite)
        # checkpoints
        self.checkpoint_list = arcade.tilemap.process_layer(my_map, checkpoints_layer_name, TILE_SCALING,
                                                            use_spatial_hash=True)
        for sprite in self.checkpoint_list:
            self.background_list.append(sprite)

        # -- Coins
        self.coin_list = arcade.tilemap.process_layer(my_map,
                                                      coins_layer_name,
                                                      TILE_SCALING,
                                                      use_spatial_hash=True)

        # -- Don't Touch Layer
        self.dont_touch_list = arcade.tilemap.process_layer(my_map,
                                                            dont_touch_layer_name,
                                                            TILE_SCALING,
                                                            use_spatial_hash=True)

        # doors and keys
        self.golden_key_list = arcade.tilemap.process_layer(my_map,
                                                            golden_key_layer_name,
                                                            TILE_SCALING,
                                                            use_spatial_hash=True)
        self.golden_door_list = arcade.tilemap.process_layer(my_map,
                                                             golden_door_layer_name,
                                                             TILE_SCALING,
                                                             use_spatial_hash=True)

        # --- Other stuff
        # Set the background color
        if my_map.background_color:
            arcade.set_background_color(my_map.background_color)
            self.background_color = my_map.background_color
        else:
            self.background_color = arcade.csscolor.PURPLE

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
        self.golden_key_list.draw()
        self.golden_door_list.draw()
        self.wall_list.draw()
        self.moving_traps_list.draw()
        self.enemy_list.draw()
        self.background_list.draw()
        self.wall_list.draw()
        self.coin_list.draw()
        self.dont_touch_list.draw()
        self.player_list.draw()
        self.foreground_list.draw()
        self.ladder_list.draw()

        # Draw our score on the screen, scrolling it with the viewport

        score_text = f"Score: {self.score}"
        arcade.draw_text(score_text, 20 + self.view_left, SCREEN_HEIGHT - 30 + self.view_bottom,
                         arcade.csscolor.BLACK, 18)
        arcade.draw_text(f'Level {self.level}', 20 + self.view_left, SCREEN_HEIGHT - 50 + self.view_bottom,
                         arcade.csscolor.BLACK, 18)
        arcade.draw_text('Pasha +PLUS+', self.player_sprite.left - 32, self.player_sprite.top, arcade.csscolor.WHITE,
                         18)
        arcade.draw_text(f"Lifes: {self.lifes}", 20 + self.view_left, SCREEN_HEIGHT - 70 + self.view_bottom,
                         arcade.csscolor.BLACK, 18)
        if self.has_golden_key:
            arcade.draw_text('Золотой ключ', 20 + self.view_left, SCREEN_HEIGHT - 90 + self.view_bottom,
                             arcade.csscolor.BLACK, 18)

    def process_keychange(self):
        """
        Called when we change a key up/down or we move on/off a ladder.
        """
        # Process up/down
        if self.up_pressed and not self.down_pressed:
            if self.physics_engine.is_on_ladder():
                self.player_sprite.change_y = PLAYER_MOVEMENT_SPEED
            elif self.physics_engine.can_jump() and not self.jump_needs_reset:
                self.player_sprite.change_y = PLAYER_JUMP_SPEED
                self.jump_needs_reset = True
                arcade.play_sound(self.jump_sound)
        elif self.down_pressed and not self.up_pressed:
            if self.physics_engine.is_on_ladder():
                self.player_sprite.change_y = -PLAYER_MOVEMENT_SPEED


        # Process up/down when on a ladder and no movement
        if self.physics_engine.is_on_ladder():
            if not self.up_pressed and not self.down_pressed:
                self.player_sprite.change_y = 0
            elif self.up_pressed and self.down_pressed:
                self.player_sprite.change_y = 0

        # Process left/right
        if self.right_pressed and not self.left_pressed:
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED
        elif self.left_pressed and not self.right_pressed:
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
        else:
            self.player_sprite.change_x = 0

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
            # if time.time() - self.timing_of_death > 0.5:
            #     self.not_immune = True
            #self.timing_of_death = time.time()
            arcade.play_sound(self.game_over_sound)
            if self.score:
                self.score -= 1
            if self.lifes:
                self.lifes -= 1
            else:
                over_view = GameOverView(self, self.background_color)
                self.window.show_view(over_view)
            self.player_sprite.change_x = 0
            self.player_sprite.change_y = 0
            self.player_sprite.center_x = self.checkpoint_x
            self.player_sprite.bottom = self.checkpoint_y

            self.left_pressed = False
            self.right_pressed = False
            self.up_pressed = False
            self.down_pressed = False
            self.jump_needs_reset = False

            # Set the camera to the start
            self.view_left = 0
            self.view_bottom = 0
            # if self.not_immune:
            #     arcade.play_sound(self.game_over_sound)
            #     if self.score:
            #         self.score-=1
            #     if self.lifes:
            #         self.lifes -= 1
            #     else:
            #         over_view = GameOverView(self, self.background_color)
            #         self.window.show_view(over_view)
            #     self.not_immune = False

        """ Movement and game logic """
        # Calculate speed based on the keys pressed


        # Move the player with the physics engine
        self.physics_engine.update()

        # Update walls, used with moving platforms
        self.wall_list.update()
        # update enemies
        self.moving_traps_list.update()
        self.enemy_list.update()

        # Check each moving trap
        for enemy in self.moving_traps_list:
            # If the trap hits a wall, reverse
            if arcade.check_for_collision_with_list(enemy, self.wall_list):
                enemy.change_x *= -1
                enemy.change_y *= -1
            # If the enemy hit the left boundary, reverse
            elif enemy.boundary_left and enemy.left < enemy.boundary_left and enemy.change_x < 0:
                enemy.change_x *= -1
            # If the trap hit the right boundary, reverse
            elif enemy.boundary_right and enemy.right > enemy.boundary_right and enemy.change_x > 0:
                enemy.change_x *= -1
            elif enemy.boundary_top and enemy.top > enemy.boundary_top and enemy.change_y > 0:
                enemy.change_y *= -1
            elif enemy.boundary_bottom and enemy.bottom < enemy.boundary_bottom and enemy.change_y < 0:
                enemy.change_y *= -1

        # Check each enemy
        for enemy in self.enemy_list:
            # If the enemy hits a wall, reverse
            if arcade.check_for_collision_with_list(enemy, self.wall_list):
                enemy.change_x *= -1
                enemy.change_y *= -1
            # If the enemy hit the left boundary, reverse
            elif enemy.boundary_left and enemy.left < enemy.boundary_left and enemy.change_x < 0:
                enemy.change_x *= -1
            # If the enemy hit the right boundary, reverse
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
        coin_hit_list = arcade.check_for_collision_with_list(self.player_sprite,
                                                             self.coin_list)

        # Loop through each coin we hit (if any) and remove it
        for coin in coin_hit_list:
            # Remove the coin
            coin.remove_from_sprite_lists()
            # Play a sound
            arcade.play_sound(self.collect_coin_sound)
            # Add one to the score
            self.score += 10

        # checkpoints
        for save in arcade.check_for_collision_with_list(self.player_sprite,
                                                         self.checkpoint_list):
            if self.current_checkpoint != save:
                self.current_checkpoint = save
                self.lifes = self.max_lifes
                self.checkpoint_x = save.center_x
                self.checkpoint_y = save.bottom

        # See if we hit any keys
        # Loop through each coin we hit (if any) and remove it
        for key in arcade.check_for_collision_with_list(self.player_sprite,
                                                        self.golden_key_list):
            # Remove the key
            key.remove_from_sprite_lists()
            # Play a sound
            arcade.play_sound(self.collect_coin_sound)
            # Add one to the score
            self.has_golden_key = True
        # check door
        for door in arcade.check_for_collision_with_list(self.player_sprite,
                                                         self.golden_door_list):
            if self.has_golden_key:
                self.has_golden_key = False
                # Remove the door
                door.remove_from_sprite_lists()
                self.foreground_list.append(door)
                # Play a sound
                # arcade.play_sound(self.collect_coin_sound)
            else:
                self.player_sprite.center_x -= self.player_sprite.change_x
                self.player_sprite.center_y -= self.player_sprite.change_y
        # Track if we need to change the viewport
        changed_viewport = False

        # See if the player hit an trap. If so, game over.
        if arcade.check_for_collision_with_list(self.player_sprite, self.moving_traps_list):
            death()
        # See if the player hit an enemy. If so, game over.
        if arcade.check_for_collision_with_list(self.player_sprite, self.enemy_list):
            death()
        # Did the player fall off the map?
        if self.player_sprite.center_y < -100:
            death()

        # Did the player touch something they should not?
        if arcade.check_for_collision_with_list(self.player_sprite,
                                                self.dont_touch_list):
            death()

        # See if the user got to the end of the level
        if arcade.check_for_collision_with_list(self.player_sprite,
                                                self.exit_list):
            # Advance to the next level
            self.level += 1

            # Load the next level
            self.setup(self.level)

            # Set the camera to the start
            self.view_left = 0
            self.view_bottom = 0
            changed_viewport = True

        # --- Manage Scrolling ---

        # Scroll left
        left_boundary = self.view_left + LEFT_VIEWPORT_MARGIN
        if self.player_sprite.left < left_boundary:
            self.view_left -= left_boundary - self.player_sprite.left
            changed_viewport = True

        # Scroll right
        right_boundary = self.view_left + SCREEN_WIDTH - RIGHT_VIEWPORT_MARGIN
        if self.player_sprite.right > right_boundary:
            self.view_left += self.player_sprite.right - right_boundary
            changed_viewport = True

        # Scroll up
        top_boundary = self.view_bottom + SCREEN_HEIGHT - TOP_VIEWPORT_MARGIN
        if self.player_sprite.top > top_boundary:
            self.view_bottom += self.player_sprite.top - top_boundary
            changed_viewport = True

        # Scroll down
        bottom_boundary = self.view_bottom + BOTTOM_VIEWPORT_MARGIN
        if self.player_sprite.bottom < bottom_boundary:
            self.view_bottom -= bottom_boundary - self.player_sprite.bottom
            changed_viewport = True

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