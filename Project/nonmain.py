import arcade
import tkinter
import sys

# Constants of the window
SCREEN_WIDTH = tkinter.Tk().winfo_screenwidth()
SCREEN_HEIGHT = tkinter.Tk().winfo_screenheight()
SCREEN_TITLE = "Platformer"


class GameWindow(arcade.Window):
    def __init__(self):
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)
        self.set_fullscreen(True)
    def close(self):
        """ Close the Window. """
        super().close()



class MenuView(arcade.View):
    def on_show(self):
        """ This is run once when we switch to this view """
        arcade.set_background_color(arcade.csscolor.PURPLE)
        # ниже для отмены результатов скроллинга
        arcade.set_viewport(0, SCREEN_WIDTH - 1, 0, SCREEN_HEIGHT - 1)

    def on_draw(self):
        """ Draw this view """
        arcade.start_render()
        arcade.draw_text("Opening Screen", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2,
                         arcade.color.WHITE, font_size=50, anchor_x="center")
        arcade.draw_text("Press SPACE to advance.", SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 - 75,
                         arcade.color.WHITE, font_size=20, anchor_x="center")

    def on_key_press(self, key, modifiers):
        from GAME import GameView
        game_view = GameView()
        game_view.setup(game_view.level)
        self.window.show_view(game_view)


class GameOverView(arcade.View):

    def __init__(self, game_view, color):
        super().__init__()
        self.game_view = game_view
        self.color = color
        arcade.set_background_color(arcade.csscolor.SLATE_GRAY)
        # ниже для отмены результатов скроллинга
        arcade.set_viewport(0, SCREEN_WIDTH - 1, 0, SCREEN_HEIGHT - 1)

    def on_draw(self):
        """ Draw this view """
        arcade.start_render()
        arcade.draw_text("You Died", self.game_view.player_sprite.center_x, self.game_view.player_sprite.center_y +140,
                         arcade.color.WHITE, font_size=100, anchor_x="center")
        arcade.draw_text("Press SPACE to suffer again or ESC to exit.", self.game_view.player_sprite.center_x, self.game_view.player_sprite.center_y + 70,
                         arcade.color.WHITE, font_size=30, anchor_x="center")

    def on_key_press(self, key, modifiers):
        if key != arcade.key.ESCAPE:
            from GAME import GameView
            game = GameView()
            game.setup()
            self.window.show_view(game)
        else:
            self.window.close()
            sys.exit()


class PauseView(arcade.View):
    def __init__(self, game_view, color):
        super().__init__()
        self.game_view = game_view
        self.color = color

    def on_show(self):
        pass

    def on_draw(self):
        arcade.set_background_color(arcade.csscolor.GREY)
        arcade.start_render()

        #player_sprite = self.game_view.player_sprite
        #player_sprite.draw()
        self.game_view.golden_key_list.draw()
        self.game_view.golden_door_list.draw()
        self.game_view.wall_list.draw()
        self.game_view.moving_traps_list.draw()
        self.game_view.enemy_list.draw()
        self.game_view.background_list.draw()
        self.game_view.wall_list.draw()
        self.game_view.coin_list.draw()
        self.game_view.dont_touch_list.draw()
        self.game_view.player_list.draw()
        self.game_view.foreground_list.draw()
        self.game_view.ladder_list.draw()

        arcade.draw_text("PAUSED", self.game_view.player_sprite.center_x, self.game_view.player_sprite.center_y + 170,
                         arcade.color.BLACK, font_size=100, anchor_x="center")

        # Show tip to return or reset
        arcade.draw_text("Press Esc. to return",
                         self.game_view.player_sprite.center_x,
                         self.game_view.player_sprite.center_y + 90,
                         arcade.color.BLACK,
                         font_size=30,
                         anchor_x="center")
        arcade.draw_text("Press Enter to reset",
                         self.game_view.player_sprite.center_x,
                         self.game_view.player_sprite.center_y + 125,
                         arcade.color.BLACK,
                         font_size=30,
                         anchor_x="center")
        arcade.draw_text("Or BACKSPACE to exit",
                         self.game_view.player_sprite.center_x,
                         self.game_view.player_sprite.center_y + 60,
                         arcade.color.BLACK,
                         font_size=30,
                         anchor_x="center")

    def on_key_press(self, key, _modifiers):
        arcade.set_background_color(self.color)
        if key == arcade.key.ESCAPE:  # resume game
            self.window.show_view(self.game_view)
        elif key == arcade.key.ENTER:# reset game
            from GAME import GameView
            game = GameView()
            game.setup()
            self.window.show_view(game)
        elif key == arcade.key.BACKSPACE:
            self.window.close()
            sys.exit()


