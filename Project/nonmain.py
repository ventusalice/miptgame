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
    def __init__(self, a=0, b=0):
        arcade.View.__init__(self)
    def on_show(self):
        """ This is run once when we switch to this view """
        arcade.set_background_color(arcade.csscolor.GREEN)
        # ниже для отмены результатов скроллинга
        #arcade.set_viewport(0, SCREEN_WIDTH - 1, 0, SCREEN_HEIGHT - 1)

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
        arcade.draw_text("You Died", self.game_view.view_left + SCREEN_WIDTH // 2, self.game_view.view_bottom + SCREEN_HEIGHT // 2 + 140,
                         arcade.color.WHITE, font_size=100, anchor_x="center")
        arcade.draw_text("Press SPACE to suffer again", self.game_view.view_left + SCREEN_WIDTH // 2, self.game_view.view_bottom + SCREEN_HEIGHT // 2 + 60,
                         arcade.color.WHITE, font_size=30, anchor_x="center")
        arcade.draw_text("Press ENTER to reset", self.game_view.view_left + SCREEN_WIDTH // 2, self.game_view.view_bottom + SCREEN_HEIGHT // 2 + 20,
                         arcade.color.WHITE, font_size=30, anchor_x="center")
        arcade.draw_text("Press BACKSPACE to exit", self.game_view.view_left + SCREEN_WIDTH // 2, self.game_view.view_bottom + SCREEN_HEIGHT // 2 - 20,
                         arcade.color.WHITE, font_size=30, anchor_x="center")

    def on_key_press(self, key, modifiers):
        if key != arcade.key.BACKSPACE and key != arcade.key.ENTER:
            self.game_view.setup(level=self.game_view.level)
            self.window.show_view(self.game_view)
        elif key == arcade.key.ENTER:
            from GAME import GameView
            game = GameView()
            game.setup()
            self.window.show_view(game)
        else:
            self.window.close()
            sys.exit()


class LevelCompletedView(arcade.View):

    def __init__(self, game_view, color):
        super().__init__()
        self.game_view = game_view
        self.color = color
        arcade.set_background_color(color)
        # ниже для отмены результатов скроллинга
        arcade.set_viewport(0, SCREEN_WIDTH - 1, 0, SCREEN_HEIGHT - 1)

    def on_draw(self):
        """ Draw this view """
        arcade.start_render()
        arcade.draw_text(f"Congratulations! You just completed level {self.game_view.level-1}", self.game_view.view_left + SCREEN_WIDTH // 2, self.game_view.view_bottom + SCREEN_HEIGHT // 2 +140,
                         arcade.color.WHITE, font_size=50, anchor_x="center")
        arcade.draw_text(f"Press SPACE to advance to level {self.game_view.level} or BACKSPACE to exit.", self.game_view.view_left + SCREEN_WIDTH // 2, self.game_view.view_bottom + SCREEN_HEIGHT // 2 + 70,
                         arcade.color.WHITE, font_size=30, anchor_x="center")

    def on_key_press(self, key, modifiers):
        if key != arcade.key.BACKSPACE:
            self.game_view.setup(level=self.game_view.level)
            self.window.show_view(self.game_view)
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

        self.game_view.on_draw()

        arcade.draw_text("PAUSED", self.game_view.view_left + SCREEN_WIDTH // 2, self.game_view.view_bottom + SCREEN_HEIGHT // 2 + 170,
                         arcade.color.BLACK, font_size=100, anchor_x="center")

        # Show tip to return or reset
        arcade.draw_text("Press Esc. to return",
                         self.game_view.view_left + SCREEN_WIDTH // 2,
                         self.game_view.view_bottom + SCREEN_HEIGHT // 2 + 90,
                         arcade.color.BLACK,
                         font_size=30,
                         anchor_x="center")
        arcade.draw_text("Press Enter to reset",
                         self.game_view.view_left + SCREEN_WIDTH // 2,
                         self.game_view.view_bottom + SCREEN_HEIGHT // 2 + 125,
                         arcade.color.BLACK,
                         font_size=30,
                         anchor_x="center")
        arcade.draw_text("Or BACKSPACE to exit",
                         self.game_view.view_left + SCREEN_WIDTH // 2,
                         self.game_view.view_bottom + SCREEN_HEIGHT // 2 + 60,
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

