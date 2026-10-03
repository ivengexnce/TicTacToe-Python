import sys
import os
import tkinter as tk
from tkinter import messagebox, simpledialog
import random
import pygame
import time

# Initialize pygame mixer
pygame.mixer.init()

class TicTacToe:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Tic Tac Toe")

        self.sound_on = True
        self.theme = {
            'bg': 'lightyellow',
            'button_bg': 'green',
            'button_hover': 'lightblue',
            'text_color': 'black',
            'active_fg': 'blue'
        }
        self.current_player = "X"
        self.board = [""] * 9
        self.buttons = []
        self.vs_ai = False
        self.player_names = {}

        # Load sounds relative to the script location
        self.load_sounds()

        # Initial sounds
        if self.sound_on:
            self.play_sound('intro')
            self.play_sound('click')

        self.setup_game_options()
        self.create_buttons()
        self.create_sound_toggle()
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.window.mainloop()

    def load_sounds(self):
        # Use relative paths for cross-platform compatibility
        base_path = os.path.join(os.path.dirname(__file__), "sound assets")

        sound_files = {
            'draw': 'draw_sound.mp3',
            'click': 'click_sound.mp3',
            'win': 'win_sound.mp3',
            'move': 'button-pressed-38129.mp3',
            'hover': 'hover_sound.mp3',
            'intro': 'bang-140381.mp3',
            'error': 'error_sound.mp3',
            'closing': 'closing_sound.mp3'
        }

        self.sounds = {}
        for key, filename in sound_files.items():
            path = os.path.join(base_path, filename)
            try:
                self.sounds[key] = pygame.mixer.Sound(path)
            except (pygame.error, FileNotFoundError):
                print(f"Warning: Could not load sound file {path}")
                self.sounds[key] = None

    def play_sound(self, key):
        if self.sound_on and self.sounds.get(key):
            self.sounds[key].play()

    def setup_game_options(self):
        self.window.configure(bg=self.theme['bg'])

        choice = simpledialog.askstring("Game Mode", "Choose mode: \n 1) 1v1 \n 2) vs AI").lower()
        if choice == '1':
            self.play_sound('click')
            self.vs_ai = False
            self.player_names["X"] = simpledialog.askstring("Player 1 Name", "Enter Player 1 name (X):") or "Player 1"
            self.player_names["O"] = simpledialog.askstring("Player 2 Name", "Enter Player 2 name (O):") or "Player 2"
        else:
            self.vs_ai = True
            self.player_names["X"] = simpledialog.askstring("Player Name", "Enter your name (X):") or "Player 1"
            self.play_sound('click')
            self.player_names["O"] = "Computer"

            diff = simpledialog.askstring("AI Difficulty", "Choose difficulty: \n 1.Easy \n 2.Moderate \n 3.Hard").lower()
            if diff == '1':
                self.play_sound('click')
                self.ai_level = 'easy'
            elif diff == '2':
                self.play_sound('click')
                self.ai_level = 'moderate'
            elif diff == '3':
                self.play_sound('click')
                self.ai_level = 'hard'
            else:
                self.play_sound('error')
                messagebox.showerror("Error", "Invalid input. Enter valid input.")
                self.window.destroy()
                sys.exit()

    def create_buttons(self):
        for i in range(9):
            button = tk.Button(self.window, text="", font=('Comic Sans MS', 40), width=4, height=1,
                               command=lambda i=i: self.make_move(i))
            button.bind("<Enter>", lambda _, b=button: b.config(bg=self.theme['button_hover']))
            button.bind("<Leave>", lambda _, b=button: b.config(bg=self.theme['button_bg']))

            button.config(bg=self.theme['button_bg'],
                         fg=self.theme['text_color'],
                         activebackground=self.theme['button_hover'],
                         activeforeground=self.theme['active_fg'])
            button.grid(row=i // 3, column=i % 3)
            self.buttons.append(button)

    def create_sound_toggle(self):
        sound_btn = tk.Button(self.window, text="🔊", command=self.toggle_sound, font=('comic sans ms', 12))
        sound_btn.grid(row=3, column=2, sticky="e")
        sound_btn.config(bg=self.theme['bg'], fg='black', activebackground='lightblue', activeforeground='black')
        sound_btn.bind("<Enter>", lambda _, b=sound_btn: b.config(bg='lightblue'))
        sound_btn.bind("<Leave>", lambda _, b=sound_btn: b.config(bg=self.theme['bg']))
        self.sound_button = sound_btn
        self.sound_button.config(text="🔊" if self.sound_on else "🔇")

    def toggle_sound(self):
        self.sound_on = not self.sound_on
        if self.sound_on:
            self.sound_button.config(text="🔊")
            pygame.mixer.unpause()
            self.play_sound('click')
        else:
            self.sound_button.config(text="🔇")
            pygame.mixer.pause()

    def make_move(self, index):
        if self.board[index] == "":
            self.board[index] = self.current_player
            self.buttons[index].config(text=self.current_player)
            self.play_sound('move')

            if self.check_winner(self.current_player):
                self.play_sound('win')
                self.animate_win(self.current_player)
                messagebox.showinfo("Winner", f"{self.player_names[self.current_player]} wins!")
                self.reset_board()
            elif "" not in self.board:
                self.play_sound('draw')
                messagebox.showinfo("Draw", "It's a draw!")
                self.reset_board()
            else:
                self.current_player = "O" if self.current_player == "X" else "X"
                if self.vs_ai and self.current_player == "O":
                    self.window.after(500, self.ai_move)

    def ai_move(self):
        if self.ai_level == 'easy':
            move = random.choice([i for i, x in enumerate(self.board) if x == ""])
        elif self.ai_level == 'moderate':
            move = self.moderate_ai_move()
        else:
            move = self.minimax(self.board, "O")[1]
        self.make_move(move)

    def moderate_ai_move(self):
        empty = [i for i, x in enumerate(self.board) if x == ""]
        if 4 in empty:
            empty.remove(4)  # avoid the center to make it "moderate"
        return random.choice(empty)

    def minimax(self, board, player):
        opponent = "X" if player == "O" else "O"
        winner = self.get_winner(board)
        if winner == "O":
            return 1, None
        elif winner == "X":
            return -1, None
        elif "" not in board:
            return 0, None

        moves = []
        for i in range(9):
            if board[i] == "":
                board_copy = board[:]
                board_copy[i] = player
                score = self.minimax(board_copy, opponent)[0]
                moves.append((score, i))

        if player == "O":
            return max(moves)
        else:
            return min(moves)

    def get_winner(self, board):
        for a, b, c in [(0,1,2), (3,4,5), (6,7,8), (0,3,6), (1,4,7), (2,5,8), (0,4,8), (2,4,6)]:
            if board[a] == board[b] == board[c] != "":
                return board[a]
        return None

    def check_winner(self, player):
        wins = [(0,1,2), (3,4,5), (6,7,8), (0,3,6), (1,4,7), (2,5,8), (0,4,8), (2,4,6)]
        return any(self.board[a] == self.board[b] == self.board[c] == player for a,b,c in wins)

    def animate_win(self, player):
        for i in range(3):
            for a, b, c in [(0,1,2), (3,4,5), (6,7,8), (0,3,6), (1,4,7), (2,5,8), (0,4,8), (2,4,6)]:
                if self.board[a] == self.board[b] == self.board[c] == player:
                    self.buttons[a].config(bg='green')
                    self.buttons[b].config(bg='green')
                    self.buttons[c].config(bg='green')
                    self.window.update()
                    time.sleep(0.3)
                    self.buttons[a].config(bg=self.theme['bg'])
                    self.buttons[b].config(bg=self.theme['bg'])
                    self.buttons[c].config(bg=self.theme['bg'])
                    self.window.update()
                    time.sleep(0.3)

    def reset_board(self):
        self.board = [""] * 9
        for button in self.buttons:
            button.config(text="", bg=self.theme['button_bg'])
        self.current_player = "X"
        self.play_sound('intro')
        self.play_sound('hover')
        self.window.update()
        if self.sounds['intro']:
            self.window.after(1000, lambda: self.sounds['intro'].stop())

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.play_sound('closing')
            self.window.after(1000, lambda: self.sounds['closing'].stop() if self.sounds['closing'] else None)
            self.window.destroy()
            pygame.mixer.quit()
            sys.exit()

if __name__ == "__main__":
    TicTacToe()
