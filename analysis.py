# %% Imoport Packages
import re
import math
import matplotlib.pyplot as plt
from collections import defaultdict
import pandas as pd
import numpy as np
import enchant
import sys
from wordleutils import *


# %%
words = list(load_words('allwords.txt'))
answerlist = list(load_words('answers.txt'))
# %%
words_arr = list(words)
freq = letter_freq(words)

orange = []
grey = ['q','u','i','e','s','y']
green = [[2,'o'],[3,'a'],[4,'r']]


# %%
memory = create_memory()
for i in grey:
    row = letter_row(i)
    memory[row]=0.5
for i in orange:
    row = letter_row(i[1])
    col=i[0]-1
    memory[row,col]=1
for i in green:
    row = letter_row(i[1])
    col=i[0]-1
    memory[row,col]=2
memory


# %%
get_possible_words(memory, words_arr)
# %%
