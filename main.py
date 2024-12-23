import random
import time
import sys
import os
from kivy.clock import Clock
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.properties import ListProperty, ObjectProperty, BooleanProperty, StringProperty
from kivy.uix.recycleview import RecycleView
from kivy.uix.label import Label
from kivy.uix.behaviors import FocusBehavior
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.core.audio import SoundLoader

class SplashScreen(Screen):
    def on_enter(self):
        Clock.schedule_once(self.switch_to_main, 3)  # Display splash screen for 3 seconds

    def switch_to_main(self, dt):
        self.manager.current = 'main_menu'

class MainMenuScreen(Screen):
    pass

class InstructionsScreen(Screen):
    pass

class AddPlayerScreen(Screen):
    def add_player(self, name):
        if name:
            app = App.get_running_app()
            app.root.get_screen('player_lister').players.append(name)
            app.root.get_screen('player_lister').update_player_list()
            app.root.current = 'player_lister'

class RenamePlayerScreen(Screen):
    def rename_player(self, new_name):
        if new_name:
            app = App.get_running_app()
            screen = app.root.get_screen('player_lister')
            index = screen.players.index(screen.selected_player)
            screen.players[index] = new_name
            screen.selected_player = None
            screen.update_player_list()
            screen.update_buttons()
            app.root.current = 'player_lister'

import time

class GameplayScreen(Screen):
    game_status = StringProperty("")
    button_pressed = BooleanProperty(False)
    countdown_paused = BooleanProperty(True)  # Start with the timer paused

    def on_enter(self):
        self.ids.pause_timer_btn.disabled = True
        self.ids.pause_timer_btn.text = "Pause Timer"
        self.ids.pause_timer_btn.on_release = self.handle_pause_timer
        self.ids.resume_timer_btn.disabled = False
        self.ids.resume_timer_btn.text = "Resume Timer"
        self.ids.resume_timer_btn.on_release = self.handle_resume_timer
        self.start_gameplay()

    def enable_pause_timer_button(self, dt):
        self.ids.pause_timer_btn.disabled = False

    def handle_pause_timer(self):
        if not self.countdown_paused:
            self.countdown_paused = True
            self.ids.pause_timer_btn.disabled = True
            self.ids.resume_timer_btn.disabled = False

    def handle_resume_timer(self):
        if self.countdown_paused:
            self.countdown_paused = False
            self.ids.pause_timer_btn.disabled = False
            self.ids.resume_timer_btn.disabled = True
            self.update_countdown()

    def start_gameplay(self):
        self.players = App.get_running_app().root.get_screen('player_lister').players
        self.rem_giftnos = []
        self.rem_players = []
        for index, player in enumerate(self.players):
            self.rem_giftnos.append(index + 1)  # Adding 1 to start gift numbers from 1
            self.rem_players.append(player)
        
        self.gifted_players = []
        self.gifted_nos = []
        self.turn_number = 0
        self.rand_player1 = None
        self.rand_giftno1 = None
        self.rand_player2 = None
        self.rand_giftno2 = None
        self.next_turn()

    def next_turn(self, dt=None):
        if not self.rem_players:
            self.game_status = f"All players have been assigned. \n Game Over! \n Turns Played: {self.turn_number} \n Rewarded Gift Numbers: {self.gifted_nos} \n Rewarded Players: {self.gifted_players}"
            self.ids.pause_timer_btn.text = "Return to Main Menu"
            self.ids.pause_timer_btn.on_release = self.return_to_main_menu
            self.ids.resume_timer_btn.text = "Return to Main Menu"
            self.ids.resume_timer_btn.on_release = self.return_to_main_menu
            print("Game Over!")
            return

        self.turn_number += 1
        self.game_status = f"This is turn number: {self.turn_number}"
        print(f"This is turn number: {self.turn_number}")
        print(f"Remaining gift numbers: {self.rem_giftnos}")
        print(f"Remaining players: {self.rem_players}")

        if self.turn_number == 1:
            # sender
            self.rand_player1, self.rand_giftno1, self.rem_giftnos, self.gifted_nos = self.sender_randomiser(self.players, self.rem_giftnos)
            # recipient
            self.rand_player2, self.rem_players, self.gifted_players = self.recipient_randomiser(self.players, self.rem_players, self.rand_player1)
        else:
            # sender
            self.rand_player1 = self.rand_player2
            self.rand_giftno1 = self.players.index(self.rand_player1) + 1  # Get gift number for rand_player1
            if self.rand_giftno1 in self.rem_giftnos:
                self.rem_giftnos.remove(self.rand_giftno1)
            self.gifted_nos.append(self.rand_giftno1)
            # recipient
            self.rand_player2, self.rem_players, self.gifted_players = self.recipient_randomiser(self.players, self.rem_players, self.rand_player1)

        self.countdown_time = 10  # Keep the timer at 10 seconds
        Clock.unschedule(self.update_countdown)  # Unschedule any existing calls
        if self.turn_number == 1:
            self.countdown_paused = True  # Pause the timer on the first turn
        self.update_countdown()

    def update_countdown(self, dt=None):
        if self.countdown_paused:
            return  # Do nothing if the countdown is paused

        if self.countdown_time > 0:
            if self.turn_number == 1:
                self.game_status = f"Who will be the first to get presents? \n {self.countdown_time} seconds remaining"
            else:
                self.game_status = f"Who will be the next to give presents? \n {self.countdown_time} seconds remaining"
            print(f"Countdown: {self.countdown_time} seconds remaining")  # Print countdown timer
            self.countdown_time -= 1
            Clock.schedule_once(self.update_countdown, 1)
        else:
            self.game_status = f"The player named {self.rand_player1} will give the gift no.{self.rand_giftno1} to {self.rand_player2} \n ... \n You have 15 seconds to memorize this information."
            print(f"The player named {self.rand_player1} will give the gift no.{self.rand_giftno1} to {self.rand_player2}")
            print(f"Countdown: {self.countdown_time} seconds remaining")  # Print countdown timer after revealing
            Clock.schedule_once(self.next_turn, 15)  # 15-second delay before the next turn
            self.enable_pause_timer_button(None)
            self.button_pressed = False

    def recipient_randomiser(self, players, rem_players, sender):
        """
        Randomly selects a recipient from the remaining players, ensuring it's not the sender.
        """
        if not rem_players:
            raise ValueError("No remaining players.")

        eligible_recipients = [player for player in rem_players if player != sender]

        if not eligible_recipients:
            raise ValueError("No eligible recipients for this sender.")

        rand_player = random.choice(eligible_recipients)
        rem_players.remove(rand_player)
        self.gifted_players.append(rand_player)

        return rand_player, rem_players, self.gifted_players

    def sender_randomiser(self, players, rem_giftnos):
        """
        Randomly selects a gift number for the sender and updates gift number lists.
        """
        if not rem_giftnos:
            raise ValueError("No remaining gift numbers.")

        rand_giftno = random.choice(rem_giftnos)
        rem_giftnos.remove(rand_giftno)
        self.gifted_nos.append(rand_giftno)
        rand_player = players[rand_giftno - 1]  # Adjust index for 0-based list

        return rand_player, rand_giftno, rem_giftnos, self.gifted_nos

    def return_to_main_menu(self):
        self.manager.current = 'main_menu'

class SelectableLabel(RecycleDataViewBehavior, Label):
    index = None
    selected = BooleanProperty(False)
    selectable = BooleanProperty(True)

    def refresh_view_attrs(self, rv, index, data):
        self.index = index
        return super(SelectableLabel, self).refresh_view_attrs(rv, index, data)

    def apply_selection(self, rv, index, is_selected):
        self.selected = is_selected
        self.canvas.before.clear()
        with self.canvas.before:
            Color(0, 0.5, 0.5, 1) if is_selected else Color(0.25, 0.5, 0.5, 1)
            Rectangle(pos=self.pos, size=self.size)

class PlayerListerScreen(Screen):
    players = ListProperty([])
    selected_player = ObjectProperty(None, allownone=True)
    selected_gno = ObjectProperty(None, allownone=True)
    selected_name = ObjectProperty(None, allownone=True)

    def on_enter(self):
        self.update_player_list()
        self.update_buttons()

    def update_player_list(self):
        self.ids.player_list.data = [{'text': f'{idx + 1}. {player}'} for idx, player in enumerate(self.players)]
        self.update_buttons()

    def update_buttons(self):
        self.ids.delete_player_btn.disabled = self.selected_player is None
        self.ids.rename_player_btn.disabled = self.selected_player is None
        self.ids.start_game_btn.disabled = len(self.players) < 3

    def select_player_by_number(self, number):
        try:
            number = int(number)
            if number <= 0:
                raise ValueError
            if 0 < number <= len(self.players):
                self.selected_gno = number
                self.selected_name = self.players[number - 1]
                self.selected_player = self.selected_name
                self.update_buttons()
        except ValueError:
            raise ValueError("Invalid Value Error: the value must be a positive integer.")

    def delete_player(self):
        if self.selected_player:
            updated_list = self.players[:]
            removed_item = updated_list.pop(self.selected_gno - 1)
            self.players = updated_list
            self.selected_player = None
            self.selected_gno = None
            self.selected_name = None
            self.update_player_list()
            self.update_buttons()

#kv = Builder.load_file('main_menu.kv')

if getattr(sys, 'frozen', False):  # Check if running as a PyInstaller bundle
    # If running as a bundle, use the path to the executable
    kv_file = os.path.join(sys._MEIPASS, 'main_menu.kv')
else:
    # If running in a normal Python environment, use the current directory
    kv_file = 'main_menu.kv'

Builder.load_file(kv_file)

class HelloApp(App):
    def build(self):
        self.screen_manager = ScreenManager()
        self.screen_manager.add_widget(SplashScreen(name='splash'))
        self.screen_manager.add_widget(MainMenuScreen(name='main_menu'))
        self.screen_manager.add_widget(InstructionsScreen(name='instructions'))
        self.screen_manager.add_widget(PlayerListerScreen(name='player_lister'))
        self.screen_manager.add_widget(AddPlayerScreen(name='add_player'))
        self.screen_manager.add_widget(RenamePlayerScreen(name='rename_player'))
        self.screen_manager.add_widget(GameplayScreen(name='gameplay'))
        Window.bind(on_key_down=self.on_key_down)

        self.music = SoundLoader.load('music.mp3')
        if self.music:
            self.music.loop = True
            self.music.play()

        return self.screen_manager

    def toggle_music(self):
        if self.music:
            if self.music.state == 'play':
                self.music.stop()
            else:
                self.music.play()

    def on_key_down(self, window, key, *args):
        if key == 27:  # Esc key
            self.screen_manager.current = 'main_menu'
            return True
        return False

    def start_new_game(self):
        self.screen_manager.current = 'player_lister'

    def show_instructions(self):
        self.screen_manager.current = 'instructions'

    def start_game(self):
        self.screen_manager.current = 'gameplay'

    def quit_game(self):
        App.get_running_app().stop()

if __name__ == '__main__':
    HelloApp().run()