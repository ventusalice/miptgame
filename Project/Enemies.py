import arcade

# Constants used to track if the enemy is facing left or right
RIGHT_FACING = 0
LEFT_FACING = 1
def load_texture_pair(filename):
    """
    Load a texture pair, with the second being a mirror image.
    """
    return [
        arcade.load_texture(filename),
        arcade.load_texture(filename, flipped_horizontally=True)
    ]

class Enemy(arcade.Sprite):
    def __init__(self, scale=1):

        # Set up parent class
        super().__init__(scale=scale)

        # Default to face-right
        self.enemy_face_direction = RIGHT_FACING

        # Used for flipping between image sequences
        self.cur_texture = 0

        self.run_textures=[[]]

    def run(self):
        pass

    def update_animation(self, delta_time: float = 1 / 60):

        # Figure out if we need to flip face left or right
        if self.change_x < 0 and self.enemy_face_direction == RIGHT_FACING:
            self.enemy_face_direction = LEFT_FACING
            self.set_hit_box(self.run_textures[0][1].hit_box_points)
        elif self.change_x > 0 and self.enemy_face_direction == LEFT_FACING:
            self.enemy_face_direction = RIGHT_FACING
            self.set_hit_box(self.run_textures[0][0].hit_box_points)

        self.run()


class Old_Guardian(Enemy):
    """ Player Sprite"""

    def __init__(self, scale=1):

        # Set up parent class
        super().__init__(scale=scale)

        # Used for flipping between image sequences
        self.change_x = 4
        # --- Load Textures ---

        main_path = "images/enemies/Old_Guardian/Old_Guardian_walk/"

        # Текстуры бега
        self.run_textures = []
        for i in range(8):
            texture = load_texture_pair(f"{main_path}Old_Guardian_walk-{i}.png")
            self.run_textures.append(texture)



        # Set the initial texture
        self.texture = self.run_textures[0][0]

        # Hit box will be set based on the first image used
        self.set_hit_box(self.texture.hit_box_points)



    def run(self):
        # Анимация бега
        self.cur_texture += 1
        if self.cur_texture > 47:
            self.cur_texture = 0
        self.texture = self.run_textures[self.cur_texture // 6][self.enemy_face_direction]
        return

class Skeleton_Lighter(Enemy):
    """ Player Sprite"""

    def __init__(self, scale=0.7):

        # Set up parent class
        super().__init__(scale=scale)

        # Used for flipping between image sequences
        self.change_x = 4
        # --- Load Textures ---

        main_path = "images/enemies/Skeleton_Lighter/SL_walk/"

        # Текстуры бега
        self.run_textures = []
        for i in range(8):
            texture = load_texture_pair(f"{main_path}SL_walk-{i}.png")
            self.run_textures.append(texture)



        # Set the initial texture
        self.texture = self.run_textures[0][0]

        # Hit box will be set based on the first image used
        self.set_hit_box(self.texture.hit_box_points)



    def run(self):
        # Анимация бега
        self.cur_texture += 1
        if self.cur_texture > 47:
            self.cur_texture = 0
        self.texture = self.run_textures[self.cur_texture // 6][self.enemy_face_direction]
        return
