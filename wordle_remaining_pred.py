# %% Imoport Packages
import enchant
import random
import time
from wordleutils import *
import pandas as pd
# %%
words = list(load_words('allwords.txt'))
answerlist = list(load_words('answers.txt'))

# %%
wordsarr = list(words)
freq_model = pd.read_csv('freq_rank.csv', header=None)
freq_model.columns=['word', 'Rank']

# %%
def play_wordle_remaining_pred(n_games, startword, startword2, wordsarr, answerlist, freq_model, random_answer=True, answer=''):
    start = time.time()
    start2 = time.process_time()
    d = enchant.Dict("en_US")
    orange_letters_hist=[]
    green_letters_hist=[]
    grey_letters_hist=[]
    memory = create_memory()
    
    if random_answer==True:
        answer = random.choice(answerlist)
        while d.check(answer)==False:
            answer = random.choice(answerlist)
            
    for i in range(1,n_games+1):
        if i == 1:
            guess = startword
        elif (i == 2) and (startword2!=''):
            guess = startword2
        else:
            matches = get_possible_words(memory, wordsarr)
            wordsarr = matches
            #matches = get_possible_words_old(wordsarr, orange_letters_hist, green_letters_hist, grey_letters_hist)
            word_scores=[]
            for word in matches:
                memory2 = memory.copy()
                match_arr = np.array([letter_row(letter) for letter in word_to_vec(word)])
                for le in match_arr:
                    if np.sum(memory2[le])==0:
                        memory2[le]=0.5
                remaining = len(get_possible_words(memory2, wordsarr))
                word_scores.append([word, remaining, int(freq_model[freq_model['word']==word]['Rank'])])
            sorted_list = sorted(word_scores, key = lambda x: (x[1], x[2]))
            guess=sorted_list[0][0]
            
        memory = encode_guess(word_to_vec(guess), word_to_vec(answer), memory)
            
            
        print("Guess: ", guess)
        print('Round: ', i)
        orange_letters, green_letters, grey_letters = wordle_game(answer, guess, i)
        if (orange_letters==1) and (green_letters==1) and (grey_letters==1):
            print('You won!')
            print(f'Time: {time.time() - start}')
            print(f'CPU Time: {time.process_time() - start2}')
            winstr=''
            prefix='\033[48;5;2m\033[38;5;232m '
            for i in guess:
                ii = prefix+i+' \033[0;0m'
                winstr+=ii
            print(winstr)
            break
        else:
            if orange_letters!=[]:
                orange_letters_hist=orange_letters_hist+orange_letters
            if green_letters!=[]:
                green_letters_hist=green_letters_hist+green_letters
            if grey_letters!=[]:
                grey_letters_hist=grey_letters_hist+grey_letters
            if (orange_letters_hist!=[]) and (green_letters_hist!=[]):
                for letterpos in orange_letters_hist:
                    if letterpos[1] in green_letters_hist:
                        orange_letters_hist.pop(letterpos)
        orange_letters_hist = [list(x) for x in set(tuple(x) for x in orange_letters_hist)]
        green_letters_hist = [list(x) for x in set(tuple(x) for x in green_letters_hist)]
        grey_letters_hist = list(set(grey_letters_hist))
        outputstr = ''
        outpos=1
        for letter in guess:
            if grey_letters!=[]:
                if letter in grey_letters:
                    string="\033[48;5;240m\033[38;5;231m "+letter+" "
            if orange_letters!=[]:
                if [outpos,letter] in orange_letters:
                    string="\033[48;5;202m\033[38;5;231m "+letter+" "
            if green_letters!=[]:
                if [outpos,letter] in green_letters:
                    string="\033[48;5;2m\033[38;5;231m "+letter+" "
            outputstr=outputstr+string+' \033[0;0m'
            outpos+=1
        print(outputstr)

        print('Orange: \033[38;5;202m\033[48;5;231m'+str(orange_letters_hist)+'\033[0;0m')
        print('Green: \033[38;5;2m\033[48;5;231m'+str(green_letters_hist)+'\033[0;0m')
        print('Grey: \033[38;5;240m\033[48;5;231m'+str(grey_letters_hist)+'\033[0;0m')
        if i == n_games:
            print('Sorry, you lost. The answer was: ', answer)
            print(f'Time: {time.time() - start}')
            print(f'CPU Time: {time.process_time() - start2}')

# %%          
if __name__=="__main__":  
    play_wordle_remaining_pred(5, 'toeas', 'unhip', wordsarr, answerlist, freq_model)
