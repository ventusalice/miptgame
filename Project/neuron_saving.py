import GAME
import arcade
import pickle
import copy

f = open('./bank/0_number', 'r')
bank_number=int(f.read())
f.close()

class NeuronSave(GAME.GameView):
    def __init__(self):
        GAME.GameView.__init__(self)
        self.exit_list_list = []
        self.dont_touch_list_list = []
        self.enemy_list_list = []
        self.wall_list_list = []
        self.coin_list_list = []
        self.heart_list_list = []
        self.golden_key_list_list = []
        self.golden_door_list_list = []
        self.player_list_list = []
        self.left_pressed_list = []
        self.right_pressed_list = []
        self.up_pressed_list = []
        self.down_pressed_list = []
        self.dash_pressed_list = []
        
    
    def on_update(self, delta_time):
        GAME.GameView.on_update(self, delta_time)
        self.exit_list_list.append(copy.copy(self.exit_list))
        self.dont_touch_list_list.append(copy.copy(self.dont_touch_list))
        self.enemy_list_list.append(copy.copy(self.enemy_list))
        self.wall_list_list.append(copy.copy(self.wall_list))
        self.coin_list_list.append(copy.copy(self.coin_list))
        self.heart_list_list.append(copy.copy(self.heart_list))
        self.golden_key_list_list.append(copy.copy(self.golden_key_list))
        self.golden_door_list_list.append(copy.copy(self.golden_door_list))
        self.player_list_list.append(copy.copy(self.player_list))
        self.left_pressed_list.append(copy.copy(self.left_pressed))
        self.right_pressed_list.append(copy.copy(self.right_pressed))
        self.up_pressed_list.append(copy.copy(self.up_pressed))
        self.down_pressed_list.append(copy.copy(self.down_pressed))
        self.dash_pressed_list.append(copy.copy(self.dash_pressed))
    
    def setup(level=0):
        GAME.GameView.setup(level)
        
                
                                      
        
def main():
    """ Main method """
    window = GAME.GameWindow()
    # game = GameView()
    view = NeuronSave()
    view.setup(level=0)
    # game.setup(game.level)
    window.show_view(view)
    arcade.run()


if __name__ == "__main__":
    main()
    
"""   
f = open(f'./bank/{bank_number}', 'w')
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False
        self.jump_needs_reset = False
        self.dash_pressed = False
        self.dash_is_ready =True
"""