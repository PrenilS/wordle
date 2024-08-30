import enchant
import random
import gradio as gr
from wordleutils import *

# Load the answer list
answerlist = list(load_words('answers.txt'))

# Initialize the keyboard
keyboard = {letter: 'white' for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'}

# Function to update keyboard colors
def update_keyboard(orange_letters, green_letters, grey_letters, keyboard):
    for pos, letter in green_letters:
        keyboard[letter.upper()] = 'green'
    for pos, letter in orange_letters:
        if keyboard[letter.upper()] != 'green':  # Don't overwrite green
            keyboard[letter.upper()] = 'orange'
    for letter in grey_letters:
        if keyboard[letter.upper()] not in ['green', 'orange']:  # Don't overwrite green or orange
            keyboard[letter.upper()] = 'grey'
    return keyboard

# Function to play the game
def play_wordle_manual(guess, answer='', random_answer=True):
    d = enchant.Dict("en_US")
    
    if not hasattr(play_wordle_manual, 'answer'):
        # Initialize the answer, histories, and keyboard on the first run
        if random_answer:
            answer = random.choice(answerlist)
            while not d.check(answer):
                answer = random.choice(answerlist)
        play_wordle_manual.answer = answer
        play_wordle_manual.orange_letters_hist = []
        play_wordle_manual.green_letters_hist = []
        play_wordle_manual.grey_letters_hist = []
        play_wordle_manual.keyboard = {letter: 'white' for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'}
        play_wordle_manual.guess_history = []
    
    # Validation for the guess
    if len(guess) != 5 or not d.check(guess):
        return "Please only use 5 English letter words.", display_keyboard(play_wordle_manual.keyboard), display_guess_history(play_wordle_manual.guess_history)
    
    # Extract answer and histories
    answer = play_wordle_manual.answer
    orange_letters_hist = play_wordle_manual.orange_letters_hist
    green_letters_hist = play_wordle_manual.green_letters_hist
    grey_letters_hist = play_wordle_manual.grey_letters_hist
    keyboard = play_wordle_manual.keyboard
    guess_history = play_wordle_manual.guess_history
    
    # Game logic
    orange_letters, green_letters, grey_letters = wordle_game(answer, guess, 1)
    if green_letters == [[i+1, c] for i, c in enumerate(answer)]:
        play_wordle_manual.answer = None  # Reset answer to trigger new game
        keyboard = update_keyboard(orange_letters, green_letters, grey_letters, keyboard)
        guess_history.append(format_guess(guess, orange_letters, green_letters, grey_letters))
        return f"You won! The correct word was {answer}", display_keyboard(keyboard), display_guess_history(guess_history)
    else:
        # Update history and keyboard
        if orange_letters:
            orange_letters_hist.extend(orange_letters)
        if green_letters:
            green_letters_hist.extend(green_letters)
        if grey_letters:
            grey_letters_hist.extend(grey_letters)
        
        # Remove duplicates
        orange_letters_hist = [list(x) for x in set(tuple(x) for x in orange_letters_hist)]
        green_letters_hist = [list(x) for x in set(tuple(x) for x in green_letters_hist)]
        grey_letters_hist = list(set(grey_letters_hist))
        
        # Update the keyboard
        keyboard = update_keyboard(orange_letters, green_letters, grey_letters, keyboard)
        
        # Add the guess to the history
        guess_history.append(format_guess(guess, orange_letters, green_letters, grey_letters))
        
        return "", display_keyboard(keyboard), display_guess_history(guess_history)

# Function to display the keyboard
def display_keyboard(keyboard):
    rows = ['QWERTYUIOP', 'ASDFGHJKL', 'ZXCVBNM']
    keyboard_html = '<div style="font-family:monospace;">'
    for row in rows:
        keyboard_html += '<div style="margin-bottom:5px;">'
        for letter in row:
            color = keyboard[letter]
            keyboard_html += f"<span style='background-color:{color}; padding:5px; margin:2px; border-radius:5px;'>{letter}</span>"
        keyboard_html += '</div>'
    keyboard_html += '</div>'
    return keyboard_html

# Function to format a guess for display
def format_guess(guess, orange_letters, green_letters, grey_letters):
    formatted_guess = ""
    for i, letter in enumerate(guess):
        if [i+1, letter] in green_letters:
            formatted_guess += f"<span style='background-color:green; padding:5px; margin:2px; border-radius:5px;'>{letter}</span>"
        elif [i+1, letter] in orange_letters:
            formatted_guess += f"<span style='background-color:orange; padding:5px; margin:2px; border-radius:5px;'>{letter}</span>"
        elif letter in grey_letters:
            formatted_guess += f"<span style='background-color:grey; padding:5px; margin:2px; border-radius:5px;'>{letter}</span>"
        else:
            formatted_guess += f"<span style='padding:5px; margin:2px; border-radius:5px;'>{letter}</span>"
    return formatted_guess

# Function to display the guess history
def display_guess_history(guess_history):
    history_html = '<div style="font-family:monospace; margin-top:20px;">'
    for guess in guess_history:
        history_html += f"<div>{guess}</div>"
    history_html += '</div>'
    return history_html

# Create Gradio Interface
iface = gr.Interface(fn=play_wordle_manual, 
                     inputs="text", 
                     outputs=["html", "html", "html"],
                     title="Wordle Game",
                     description="Enter a 5-letter word to play Wordle")

# Launch the web app
iface.launch()
