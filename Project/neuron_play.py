import GAME
import pickle
import sklearn
import nonmain
import arcade

def flatten2list(object_list):
    gather = []
    for item in object_list:
        if isinstance(item, (list, tuple, set)):
            gather.extend(flatten2list(item))            
        else:
            gather.append(item)
    return gather

def elongate(object_list):
    return object_list + [0.0]*(10000 - len(object_list))

class NeuronPlay(GAME.GameView):
    def __init__(self):
        GAME.GameView.__init__(self)
        with open('./net.dump', 'rb') as f:
            self.net = pickle.load(f)
        
    def on_update(self, delta_time):
        X = [elongate(flatten2list([[[i.position, i.collision_radius, i.velocity] for i in (lambda x: [] if x == None else x)(lists)] for lists in [self.exit_list,
                                                                                                      self.player_list,                                                              
                                                                                                      self.dont_touch_list,
                                                                                                      self.enemy_list,
                                                                                                      self.wall_list,
                                                                                                      self.coin_list,
                                                                                                      self.heart_list,
                                                                                                      self.golden_key_list,
                                                                                                      self.golden_door_list,
                                                                                                      self.ladder_list]]))]
        
        #print(X)
        result = self.net.predict(X)
        #print(result)
        self.left_pressed, self.right_pressed, self.up_pressed, self.down_pressed, self.dash_pressed = [i == 'True' for i in str(result[0]).split(',')]
        #print([self.left_pressed, self.right_pressed, self.up_pressed, self.down_pressed, self.dash_pressed])
        GAME.GameView.on_update(self, delta_time)
        self.process_keychange()    
            
    def on_keychange(self, key, modifiers):
        if key == arcade.key.R:
            self.setup(self.level)
        if key == arcade.key.ESCAPE:
            gpause = nonmain.PauseView(self, self.background_color)
            self.window.show_view(gpause)
            
            
def main():
    """ Main method """
    window = GAME.GameWindow()
    # game = GameView()
    view = NeuronPlay()
    view.setup(level=8)
    # game.setup(game.level)
    window.show_view(view)
    arcade.run()


if __name__ == "__main__":
    main()