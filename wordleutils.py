import pandas as pd
import re
import numpy as np
# %% Load words
def load_words(file):
    file_to_open = file
    with open(file_to_open) as word_file:
        valid_words = set(word_file.read().split())
    return valid_words

def letter_freq(wordlist):
    freq = {}
    for word in wordlist:
        pos = 1
        for letter in word:
            letter = letter.lower()
            if letter in freq.keys():
                freq[letter][pos-1]+=1
            else:
                freq[letter]=[0, 0, 0, 0, 0]
                freq[letter][pos-1]+=1
            pos += 1
    freq_df = pd.DataFrame(freq).T
    freq_df.columns=['1','2','3','4','5']
    freq_df['total']=freq_df['1']+freq_df['2']+freq_df['3']+freq_df['4']+freq_df['5']
    return freq_df

def word_to_vec(word):
    return np.array(list(word))

def create_memory():
    return np.zeros([26, 5])

def letter_row(letter):
    return ord(letter)-97

def encode_guess(guess_arr, answer_arr, memory):
    intersect = np.in1d(guess_arr, answer_arr)
    ind_g = np.arange(guess_arr.shape[0])[intersect]
    guess_arr_encoded = np.array([0.5,0.5,0.5,0.5,0.5])
    for i in ind_g:
        if guess_arr[i]==answer_arr[i]:
            guess_arr_encoded[i]=2
        else:
            guess_arr_encoded[i]=1
    
    for i, v in enumerate(guess_arr_encoded):
        row = letter_row(guess_arr[i])
        col = i
        # grey means that no position has that letter
        if v == 0.5:
            memory[row]=v
        else:
            memory[row, col]=v
    print(guess_arr_encoded)
    return memory

def get_possible_words(memory, words_arr):
    #greens (2) has to be in the same position for the guess
    #oranges (1) has to be in the same row but not same position for the guess
    #greys (0.5) have to not be in the guess at all
    possible = []
    nonzero_memory = np.nonzero(memory)
    for word in words_arr:
        word_arr = np.array([letter_row(letter) for letter in word_to_vec(word)])
    
        break_outer = False
        possible_word = True
        for row in nonzero_memory[0]:
            for col in nonzero_memory[1]:
                #green
                if memory[row, col] == 2:
                    if word_arr[col] != row:
                        break_outer = True
                        possible_word = False
                        break
                #orange
                if memory[row, col] == 1:
                    if word_arr[col] == row:
                        break_outer = True
                        possible_word = False
                        break
                    if sum([x==row for x in word_arr])==0:
                        break_outer = True
                        possible_word = False
                        break
            #grey
            if memory[row, 0] == 0.5:
                if sum([x==row for x in word_arr])!=0:
                    break_outer = True
                    possible_word = False
                    break
            if break_outer == True:
                possible_word = False
                break 
        
        if possible_word == True:
            possible.append(word)
    return possible

def orange_words(orange_letters, word):
    if orange_letters==[]:
        return word
    match_all = 1
    for letterpos in orange_letters:
        pos = letterpos[0]
        letter = letterpos[1]
        pattern = "["+str(letter)+"]"
        X = re.finditer(pattern, word)
        
        try:
            next(X)
        except StopIteration:
            match = 0
        
        X = re.finditer(pattern, word)
        for x in X:
            if x:
                if x.span()[1]==pos:
                    match=0
                    break
                else:
                    match=1
            else:
                match=0
        match_all = match_all*match
    if match_all == 1:
        return word

    
def green_words(green_letters, word):
    if green_letters==[]:
        return word
    match_all = 1
    for letterpos in green_letters:
        pos = letterpos[0]
        letter = letterpos[1]
        pattern = "["+str(letter)+"]"
        X = re.finditer(pattern, word)
        
        try:
            next(X)
        except StopIteration:
            match = 0
        
        X = re.finditer(pattern, word)
        for x in X:
            if x:
                if x.span()[1]==pos:
                    match=1
                    break
                else:
                    match=0
            else:
                match=0
        match_all = match_all*match
    if match_all == 1:
        return word
    
    
def grey_words(grey_letters, green_letters, word):
    if grey_letters==[]:
        return word
    match_all = 1
    for letter in grey_letters:
        pattern = "["+str(letter)+"]"
        X = re.finditer(pattern, word)
        
        try:
            next(X)
        except StopIteration:
            match = 1
        
        X = re.finditer(pattern, word)
        for x in X:
            if x:
                match=0
                for letterpos in green_letters:
                    pos = letterpos[0]
                    letterg = letterpos[1]
                    if letterg==letter:
                        if x.span()[1]==pos:
                            match=1
                        else:
                            match=0
            else:
                match=1
            match_all = match_all*match
    if match_all == 1:
        return word
    
def get_possible_words_old(wordsarr, orange_letters, green_letters, grey_letters):
    matchesorange = []
    matchesgreen= []
    matchesgrey = []
    for word in wordsarr:
        matchorange = orange_words(orange_letters, word)
        matchgreen = green_words(green_letters, word)
        matchgrey = grey_words(grey_letters, green_letters, word)
        if matchorange:
            matchesorange.append(matchorange)
        if matchgreen:
            matchesgreen.append(matchgreen)
        if matchgrey:
            matchesgrey.append(matchgrey)
    orange_set = set(matchesorange)
    green_set = set(matchesgreen)
    grey_set = set(matchesgrey)
    return list((orange_set.intersection(green_set)).intersection(grey_set))

def score_word_new(word, memory, freq):
    guess_arr_encoded = np.array([0.5,0.5,0.5,0.5,0.5])
    guess_arr = word_to_vec(word)
    guess_score = 0
    for i, v in enumerate(guess_arr_encoded):
        row = letter_row(guess_arr[i])
        col = i
        if memory[row, col]==0:
            guess_score+=v
    return guess_score

def score_word(word, freq):
    pos = 1
    score = 0
    letters_used=[]
    for letter in word:
        if letter in letters_used:
            score += freq.loc[letter].loc[str(pos)]/2
        else:
            score += freq.loc[letter].loc[str(pos)]
        if letter in 'aeiou':
            score+=freq.loc[letter].loc[str(pos)]*0.1
        letters_used.append(letter)
        pos += 1
    return score

# %%
def wordle_game(answer, guess, round):
    orange_letters=[]
    green_letters=[]
    grey_letters=[]
    if answer == guess:
        pos = 1
        for letter in answer:
            green_letters.append([pos, letter])
        return 1,1,1
    else:
        pos = 1
        for letter in guess:
            if letter == answer[pos-1]:
                green_letters.append([pos, letter])
            else:
                if letter in answer:
                    orange_letters.append([pos, letter])
                else:
                    grey_letters.append(letter)
            pos+=1
    return orange_letters, green_letters, grey_letters