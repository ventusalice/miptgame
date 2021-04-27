import GAME
import arcade
import math

RAY_RESOLUTION = 12

class RayView(GAME.GameView):
    def __init__(self):
        super(GAME.GameView).__init__()
        self.ray_array = []
        for i in range(RAY_RESOLUTION):
            self.ray_array.append(math.tan(2*math.pi / 12 * i))
        self.ray_result = []
        
    def on_draw(self):
        super.on_draw()
        arcade.draw_line(self.player_sprite.center_x, self.player_sprite.center_y, self.player_sprite.center_x+100, self.player_sprite.center_y, arcade.color.BLACK, 2)
        
    def on_update():
        super.on_update()
        
    def setup(self, level=0):
        super(GAME.GameView).setup(self, level)
        


def main():
    """ Main method """
    window = GAME.GameWindow()
    view = RayView()
    view.__init__()
    view.setup()
    window.show_view(view)
    arcade.run()


if __name__ == "__main__":
    main()