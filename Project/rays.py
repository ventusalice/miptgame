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
        
    def on_draw():
        super.on_draw()
        arcade.draw_line(0, 500, 0, 600, arcade.color.BLACK, 2)
        
        
    def on_update():
        super.on_update()
        


def main():
    """ Main method """
    window = GAME.GameWindow()
    view = GAME.MenuView(RayView())
    window.show_view(view)
    arcade.run()


if __name__ == "__main__":
    main()