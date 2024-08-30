---
layout: post
title:  "Different levels of data, analysis and predictive analytics viewed through Wordle"
date:   2022-02-26
categories: [Python, MachineLearning, CopulaOutliers, AI]
author: Prenil Sewmohan
---

# What is the difference between Analytical, BI, Predictive and AI work?
It's not always simple and often the line is blurred. In general:
- BI is about organising and making sense of data and presenting it in a way that is fit for purpose. Data is valuable, yes, but only as valuable as what you can use it for!
- Analytics is about looking into the now useful data and identifying trends, creating insights and creating extra value on top of the already existing data by adding new variables, calculating new fields and enriching the data to make it more useful and answer specific questions about the current state of things. This can be used to inform future decisions.
- Predictive analytics learns from the specific questions being answered analytically and the decisions they influence. The aim is to try and forecast or predict what the future decision should be in a more scientific way. So if analytics explains what your current store network looks like now and indicates where there might be space for you to expand based on demographic factors, predictive analytics or data science will try to predict what the impact on your revenue will be if you did expand or will try to predict the best possible place to expand to. Crucially, this is data driven and based on past evidence.
- AI tries to take this a step further. Instead of just understanding the current state of affairs and being able to predict what might happen in order to guide decisions, we let the computer learn from its own experience and figure out what it thinks the best course of action is.

The distinctions are often grey but this article will try to illustrate the whole process via the scape goat of jumping onto the Wordle bandwagon!


## Load words
Load the accepted answers and guesses all together

```python
def load_words(file):
    file_to_open = file
    with open(file_to_open) as word_file:
        valid_words = set(word_file.read().split())
    return valid_words
```


```python
words = list(load_words('allwords.txt'))
answerlist = list(load_words('answers.txt'))
```


```python
wordsarr=list(words)
```

# Data and visualisation
Our data in this case are the word lists. What story does that data have to tell us about Wordle? 

Lets understand the frequency of letter usage per 5 letter word in the whole corpus and by position in those words. 


```python
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
```


```python
freq = letter_freq(words)
freq.head()
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>1</th>
      <th>2</th>
      <th>3</th>
      <th>4</th>
      <th>5</th>
      <th>total</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>s</th>
      <td>1565</td>
      <td>93</td>
      <td>533</td>
      <td>516</td>
      <td>3958</td>
      <td>6665</td>
    </tr>
    <tr>
      <th>t</th>
      <td>815</td>
      <td>239</td>
      <td>616</td>
      <td>898</td>
      <td>727</td>
      <td>3295</td>
    </tr>
    <tr>
      <th>u</th>
      <td>189</td>
      <td>1186</td>
      <td>667</td>
      <td>401</td>
      <td>67</td>
      <td>2510</td>
    </tr>
    <tr>
      <th>r</th>
      <td>628</td>
      <td>940</td>
      <td>1198</td>
      <td>717</td>
      <td>672</td>
      <td>4155</td>
    </tr>
    <tr>
      <th>e</th>
      <td>303</td>
      <td>1627</td>
      <td>882</td>
      <td>2327</td>
      <td>1521</td>
      <td>6660</td>
    </tr>
  </tbody>
</table>
</div>



### S, B, P, M, A, D and C are very high freq for the first letter and the vowels for the second.


```python
import seaborn as sns
ax=sns.heatmap(freq[['1','2','3','4','5']], linewidths=.5, xticklabels=1, yticklabels=1, annot=True)
plt.rcParams["figure.figsize"] = (15,30)
plt.show()
```


    
![png](/assets/images/wordleoutput_10_0.PNG)
    


### Overall letter frequencies:
The raw words have been transformed into useful and understandable information. This is useful information for deciding which guess to make. You are better off choosing guesses which combine a number of most high frequency words at each position. These are more likely to be the answer but will also eliminate the most other guesses. 


```python
sns.barplot(x=freq.index, y=freq['total'])
plt.rcParams["figure.figsize"] = (5,5)
plt.show()
```


    
![png](/assets/images/wordleoutput_12_0.PNG)
    


# Analysis
Lets add another level to this. Now that we understand the words we are dealing with and what their frequencies are, we want to use that to solve a problem. Which word should I pick? In order to answer that question, we first need to understand something about your current situation. In this case, we need to know where you are in the game and this is based on the orange, green and grey letters you have accumulated.

The first step is to filter out only the remaining possible words from the corpus. In our retail expansion parallel these two steps are very similar to first understanding the retailers current network and then being able to identify areas they have no presence in. Next, which of these areas might be worthwhile in the first place?


```python
wordsarr = list(words)
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
        # similar logic, left out for space
        return word
    
    
def grey_words(grey_letters, green_letters, word):
        # also left out for space
        return word
```

### Test a scenario
only show words matching all 3 constraints


```python
def get_possible_words(wordsarr, orange_letters, green_letters, grey_letters):
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
```

Orange: n at position 3 and y at position y

Grey: s,o,r,e,s,c,a,t

Green: y at position 2


```python
orange = [[3,'n'],[5,'y']]
grey = ['s','o','r','e','s','c','a','t']
green = [[2,'y']]  
matches = get_possible_words(wordsarr, orange, green, grey)
```


```python
matches
```




    ['lying', 'vying', 'hying', 'nymph', 'kylin', 'dying', 'nying']



### Which one to choose? - creating insight
Great, we can understand the current situation and make suggestions based on the gaps.

Well this is where analysis start to create new data and insights by using the groundwork from before. Of the remaining words, we already know that there are big differences in the distribution of letters over 5-letter words, so we want to pick the word with the most high frequency letters out of those left.

Additionally, we value vowels more since we want to eliminate as many as we can. So lets add the frequencies of each letter for its position in the possible guess and add a little extra for vowels. The total 'score' is what we will use to flag the most 'valuable' word to choose.


```python
def score_word(word, freq):
    pos = 1
    score = 0
    letters_used=[]
    for letter in word:
        score += freq.loc[letter].loc[str(pos)]
        if letter in 'aeiou':
            score+=freq.loc[letter].loc[str(pos)]*0.1
        letters_used.append(letter)
        pos += 1
    return score
```


```python
if matches:
    word_scores=[]
    for word in matches:
        word_scores.append([word, score_word(word, freq)])

    word_scores=pd.DataFrame(word_scores)
    word_scores.columns=['word', 'score']
    word_scores=word_scores.sort_values(by=['score'],ascending=False)
    print(word_scores.head())
else:
    print('No guesses')
```

        word  score
    5  dying   2968
    4  kylin   2930
    0  lying   2859
    2  hying   2770
    6  nying   2602
    

### Based on how likely it is to have seen each letter in each of the matched words in the positions they appear, dying would seem to be the best choice. In this case, it was the right answer too.

# Predictive analytics / data science
Right now, we look at the current point in time and we understand the lay of the land and present the options available and try to help rank those by generating insights about each option.

Predictive analytics identifies where a statistical model can replace human judgement. It takes a regular set of inputs and uses those to optimise some function indicating how well you are performing and thereby 'predicts' the best output given the input.


Data science can be applied at different levels. If we wanted to predict with certainty the best guess for every possible position, that would be similar to the parallel world where we are trying to predict not just how much revenue you might make from expanding but trying to predict exactly where you should expand to. That is a hard problem and requires a lot of good data.
Ideally, we would be able to observe hundreds of thousands of games being played and have recorded for each and every turn, the number of the turn, the orange, green and grey letters accumulated and the choice that the person made. A data scientist would then take this data and
- figure out how best to structure this abnormal input data into something tabular which can be fed into a statistical model
- figure out how to code the answers themselves to fit into a model. In this case you probably make each possible word its own category and predict the probability for each category. But with over 10,000 categories, you would need a truely, truely MASSIVE amount of data where you see each possible answer at least a few times in order to get anything useful. And even then, it would be hard.
But lets take a step back, data science can also be used to try and scientifically predict the revenue instead of just inferring what it might be based on the insights we have created so far. Back in the world of Wordle, that translates to being able to more scientifically predict the best option out of the remaining possiblilities.

Our scoring function is a best analytical guess at what words are more 'typical' 5 letter words. This is a human judgement which can be replaced by a predictive model. Can we understand 'typical' more mathematically? 

While our green, grey and orange lists of letters and lists of lists are understandable, they are too loose for predictive work. A data scientist will need to figure out how best to represent the information in a way that if both efficient to compute and useable in modelling while trying to remain understandable. So we are getting rid of our lists and creating a a 26 X 5 matrix which can represent single words (a 1 in row 2 and column 3 if there is a 'B' as the third letter of the word) or a 'memory' of what we have already seen (2 represents green letters, 1 orange, 0.5 grey and 0 for those we havent seen).


I create these as functions in a seperate script (wordleutils) in the interest of space. While we are at it, we also create some scaffolding to let us actually play the game instead of looking at one scenario at a time. But more on that later!


## Copula Based Outlier Detection
In looking for a way to replace the frequency scores with a real model, I stumbled upon this very good post https://towardsdatascience.com/finding-the-best-wordle-opener-with-machine-learning-ce81331c5759
The author restructures their data in a very similar way to what we have tried. They then use outlier detection to try and predict which words are NOT outliers in the pool of all 5 letter words instead of using a sum of frequencies. Lets recreate the approach.


```python
from wordleutils import *
word_letter_freq = np.zeros([len(wordsarr), 26*5])
rw = 0
for word in wordsarr:
    word_arr = np.array([letter_row(letter) for letter in word_to_vec(word)])
    for position, letter in enumerate(word_arr):
        col = letter*5+position
        word_letter_freq[rw, col]=1
    rw += 1

colnames=[]
for l in 'abcdefghijklmnopqrstuvwxyz':
    for p in [0,1,2,3,4]:
        colnames.append(l+str(p))
word_letter_freq = pd.DataFrame(word_letter_freq, index=wordsarr, columns=colnames)
word_letter_freq.head()
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>a0</th>
      <th>a1</th>
      <th>a2</th>
      <th>a3</th>
      <th>a4</th>
      <th>b0</th>
      <th>b1</th>
      <th>b2</th>
      <th>b3</th>
      <th>b4</th>
      <th>...</th>
      <th>y0</th>
      <th>y1</th>
      <th>y2</th>
      <th>y3</th>
      <th>y4</th>
      <th>z0</th>
      <th>z1</th>
      <th>z2</th>
      <th>z3</th>
      <th>z4</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>sture</th>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>...</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
    </tr>
    <tr>
      <th>kempt</th>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>...</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
    </tr>
    <tr>
      <th>mowra</th>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>1.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>...</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
    </tr>
    <tr>
      <th>ranch</th>
      <td>0.0</td>
      <td>1.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>...</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
    </tr>
    <tr>
      <th>incog</th>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>...</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
    </tr>
  </tbody>
</table>
<p>5 rows × 130 columns</p>
</div>


### contamination is supposed to be a measure of the proportion of outliers in the data.
Lets try to quantify how many outliers we think our dataset has.


```python
word_scores=[]
for word in wordsarr:
    word_scores.append([word, score_word(word, freq)])
word_scores=pd.DataFrame(word_scores)
word_scores.columns=['word', 'score']
word_scores=word_scores.sort_values(by=['score'],ascending=False)
```


```python
word_scores['score']=pd.to_numeric(word_scores['score'])
word_scores['score'].describe(include=['object', 'float', 'int'])
```




    count    12966.000000
    mean      5801.071495
    std       1897.872627
    min       1110.300000
    25%       4321.750000
    50%       5483.600000
    75%       7271.000000
    max      11586.300000
    Name: score, dtype: float64




```python
#stupid outlier count
iqr = 7249.300000 - 4312.775000
outliers = sum(word_scores['score']< 4312.775000-1.5*iqr)+sum(word_scores['score']> 7249.300000+1.5*iqr)
total = len(word_scores)
print(total, outliers, outliers/total)
```

    12966 0 0.0
    

None of them are outliers using the IQR rule of thumb. Lets look at the distribution which is not at all Guassian. It's bi-modal.


```python
plt.hist(word_scores['score'], density=True, bins=50)
plt.rcParams["figure.figsize"] = (5,5)
plt.show()
```


    
![png](/assets/images/wordleoutput_33_0.PNG)
    


### lets use the answer list distribution to gauge outliers
While the dataset of allowed words has 2 different modes, this may be a result of there being many 'odd' words allowed as guesses. What we are actually interested in is how many of those are outliers based on the distribution of the more 'normal' answer words. Lets look at the distribution for the answers.


```python
word_scores2=[]
for word in answerlist:
    word_scores2.append([word, score_word(word, freq)])
word_scores2=pd.DataFrame(word_scores2)
word_scores2.columns=['word', 'score']
word_scores2=word_scores2.sort_values(by=['score'],ascending=False)
plt.hist(word_scores2['score'], density=True, bins=50)
plt.rcParams["figure.figsize"] = (5,5)
plt.show()
```


    
![png](/assets/images/wordleoutput_35_0.PNG)
    



```python
word_scores2['score'].describe(include=['object', 'float', 'int'])
```




    count    2309.000000
    mean     4754.309485
    std      1127.837065
    min      1698.300000
    25%      3952.600000
    50%      4698.200000
    75%      5502.200000
    max      8857.300000
    Name: score, dtype: float64




```python
iqr = 5502.200000 - 3952.600000
outliers = sum(word_scores['score']< 3952.600000-1.5*iqr)+sum(word_scores['score']> 5502.200000+1.5*iqr)
total = len(word_scores)
print(total, outliers, outliers/total)
```

    12966 2318 0.17877525836803948
    

## Much better. Lets try 17%
17% of the allowed guesses are outliers for the answer data. Based on this analysis, 'bones' is the most 'typical' word in the data to choose when there is no other information. This will become our first guess.


```python
from pyod.models.copod import COPOD
copod_model = COPOD(contamination=0.17)
copod_model.fit(word_letter_freq)
```




    COPOD(contamination=0.17, n_jobs=1)




```python
word_letter_freq['score'] = copod_model.decision_scores_
word_letter_freq.sort_values('score',inplace=True)
word_letter_freq['rank'] = range(1,len(word_letter_freq)+1)
```


```python
word_letter_freq['rank'].to_csv('freq_rank.csv')
word_letter_freq['rank'].head()
```


    bones    1
    sains    2
    rones    3
    sades    4
    geres    5
    Name: rank, dtype: int32



## lets see how it works with the same example as before but with a little less information. It was a bit too constrained already.


```python
orange = [[3,'n']]
grey = ['c','a','t']
green = []
```


```python
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
```
    Our games 'memory' looks like this.



    array([[0.5, 0.5, 0.5, 0.5, 0.5],
           [0. , 0. , 0. , 0. , 0. ],
           [0.5, 0.5, 0.5, 0.5, 0.5],
           [0. , 0. , 0. , 0. , 0. ],
           [0. , 0. , 0. , 0. , 0. ],
           [0. , 0. , 0. , 0. , 0. ],
           [0. , 0. , 0. , 0. , 0. ],
           [0. , 0. , 0. , 0. , 0. ],
           [0. , 0. , 0. , 0. , 0. ],
           [0. , 0. , 0. , 0. , 0. ],
           [0. , 0. , 0. , 0. , 0. ],
           [0. , 0. , 0. , 0. , 0. ],
           [0. , 0. , 0. , 0. , 0. ],
           [0. , 0. , 1. , 0. , 0. ],
           [0. , 0. , 0. , 0. , 0. ],
           [0. , 0. , 0. , 0. , 0. ],
           [0. , 0. , 0. , 0. , 0. ],
           [0. , 0. , 0. , 0. , 0. ],
           [0. , 0. , 0. , 0. , 0. ],
           [0.5, 0.5, 0.5, 0.5, 0.5],
           [0. , 0. , 0. , 0. , 0. ],
           [0. , 0. , 0. , 0. , 0. ],
           [0. , 0. , 0. , 0. , 0. ],
           [0. , 0. , 0. , 0. , 0. ],
           [0. , 0. , 0. , 0. , 0. ],
           [0. , 0. , 0. , 0. , 0. ]])



## Frequency based
Analytically, what the insight pointed to


```python
matches = get_possible_words(memory, wordsarr)
word_scores=[]
for word in matches:
    word_scores.append([word, score_word(word, freq)])
    #word_scores.append([word, score_word(word, memory, freq)])
sorted_list = sorted(word_scores, key = lambda x: (x[1]), reverse=True)
print(sorted_list[0:10])
```

    [['noles', 9996.3], ['sorns', 9814.6], ['noses', 9681.3], ['nomes', 9659.3], ['snies', 9583.8], ['nodes', 9538.3], ['snees', 9397.9], ['noyes', 9361.3], ['noxes', 9281.3], ['porns', 9107.6]]
    

## Model based
Predictively, what does the data tell us, is the best choice?

```python
freq_model = pd.read_csv('freq_rank.csv', header=None)
freq_model.columns=['word', 'Rank']
```

```python
word_scores=[]
for word in matches:
    word_scores.append([word, int(freq_model[freq_model['word']==word]['Rank'])])
    #word_scores.append([word, score_word(word, memory, freq)])
sorted_list = sorted(word_scores, key = lambda x: (x[1]), reverse=False)
print(sorted_list[0:10])
```

    [['sorns', 36], ['perns', 119], ['snies', 171], ['morns', 200], ['siens', 224], ['poons', 243], ['noles', 259], ['boons', 279], ['beins', 343], ['porns', 389]]
    

## Quite different but they converge very well as we add more information. Lets test them!
First... we need a way to play the game

## Game with manual input
Some code to give you the general idea. We will just import from seperate scripts for the games played by the computer


```python
from wordleutils import *
def play_wordle_manual(n_games, answerlist, answer='', random_answer=True):
    d = enchant.Dict("en_US")
    if random_answer==True:
        answer = random.choice(answerlist)
        while d.check(answer)==False:
            answer = random.choice(answerlist)
    orange_letters_hist=[]
    green_letters_hist=[]
    grey_letters_hist=[]
    for i in range(1,n_games+1):
        guess = input("What is your guess? ")
        while (len(guess)!=5) and (d.check(guess)==False):
            print('Please only use 5 english letter words')
            guess = input("What is your guess? ")
        orange_letters, green_letters, grey_letters = wordle_game(answer, guess, i)
        print("Guess: ", guess)
        print('Round: ', i)
        orange_letters, green_letters, grey_letters = wordle_game(answer, guess, i)
        if (orange_letters==1) and (green_letters==1) and (grey_letters==1):
            print('You won!')
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
                    string="\033[48;5;240m\033[38;5;231m "+letter+" \033[0;0m"
            if orange_letters!=[]:
                if [outpos,letter] in orange_letters:
                    string="\033[48;5;202m\033[38;5;231m "+letter+" \033[0;0m"
            if green_letters!=[]:
                if [outpos,letter] in green_letters:
                    string="\033[48;5;2m\033[38;5;231m "+letter+" \033[0;0m"
            outputstr=outputstr+string+' \033[0;0m'
            outpos+=1
        print(outputstr)

        print('Orange: \033[38;5;202m\033[48;5;231m'+str(orange_letters_hist)+'\033[0;0m')
        print('Green: \033[38;5;2m\033[48;5;231m'+str(green_letters_hist)+'\033[0;0m')
        print('Grey: \033[38;5;240m\033[48;5;231m'+str(grey_letters_hist)+'\033[0;0m')
        if i == n_games:
            print('Sorry, you lost. The answer was: ', answer)
```


```python
play_wordle_manual(5, answerlist, 'clogs', False)
```

![png](/assets/images/wordle1.PNG)

### Nice! We can play a full game. Let's hand the controler over to our predictive model and see how well it does.


```python
from wordle_freq import play_wordle_freq
from wordle_freq_pred import play_wordle_freq_pred
```


```python
answer = 'limes'
```

### original


```python
play_wordle_freq(5, wordsarr, answerlist, freq, False, answer)
```

![png] (/assets/images/wordle3.PNG)
    

### predictive


```python
play_wordle_freq_pred(5, wordsarr, answerlist, freq_model, False, answer)
```

![png](/assets/images/wordle4.PNG)
    

## Comparison
They take different paths and the initial insight was good so they still often get to the same answer. The predictive model sometimes gets words the analytical one doesnt but without testing all words, it is hard to say what the improvement is

# AI / data science
Now... can we create something which isin't me trying to 'guess' what the best aproach is for it? Can we just let it play the game and learn on its own?

Although our computer has been playing the game itself. It has been just making predictions about what it thinks the next best guess is based on the past either by using a probabilistic model to predict the future or by doing analysis of the words and using that understanding to create a non-probabilistic approach. Getting to real time AI is more the scenario where the computer is aware of where it is in the game and what has happened so far and tries to make guesses that get it closer to its goal. Just like we would. 

One way of doing this would be to get the computer to play the game itself millions of times over and instead of forcing it to making only guesses we think are reasonable, let it guess whatever it wants but add some uncertainty to what it guesses. We then record every single decision it makes, the state of the game at that point and the final outcome. The state in this case would be out 'memory' array and the outcome some combination of whether it won or not and how much new information its guess created. Over time, we then build up a tree of decisions where each split is a game state and as we stumble upon better and better guesses for each state, we update the path we take from that state. Eventually, we will have a very good AI. But needless to say, that would take a HUGE amount of time and i have a day job and also i dont have a super computer.

Instead, we can say that one 'goal' to pursue which is more easily measureable is how many remaining guesses are possible. If the computer just always tries to make a guess which reduces this bu the largest amount each time, it should move towards a solution. The one thing this 'agent' lacks, however, is that it never learns from its past. The agent described in the paragraph above, would get better over time. The approach below is still quite close to a predictive data science approach but it tries to take some inspiration from what a more complex AI might try to do.

## Now that we can play a full game with our code, lets work on this part to choose the word not through frequency score but based on how many of the remaining words it excludes.
```python
matches = get_possible_words(wordsarr, orange_letters_hist, green_letters_hist, grey_letters_hist)
word_scores=[]
for word in matches:
    word_scores.append([word, score_word(word, freq)])
word_scores=pd.DataFrame(word_scores)
word_scores.columns=['word', 'score']
word_scores=word_scores.sort_values(by=['score'],ascending=False)
guess=str(word_scores['word'].iloc[0])
```

# One way (almost certainly not the best way) 
### would be to take each possible word we might guess and assume all of its letters turn out to be grey. Then count how many possible words remain. The choice which results in the smallest number remaining is the one we will choose
```python
matches = get_possible_words(wordsarr, orange_letters_hist, green_letters_hist, grey_letters_hist)
word_scores=[]
for word in matches:
    grey_l2 = grey_letters_hist.copy()
    orange_l = [letter[1] for letter in orange_letters_hist]
    green_l = [letter[1] for letter in green_letters_hist]
    for letter in word:
        if (letter not in green_l) and (letter not in orange_l):
            grey_l2.append(letter)
    remaining = len(get_possible_words(wordsarr, orange_letters_hist, green_letters_hist, grey_l2))
    word_scores.append([word, remaining])
word_scores=pd.DataFrame(word_scores)
word_scores.columns=['word', 'score']
word_scores=word_scores.sort_values(by=['score'],ascending=True)
guess=str(word_scores['word'].iloc[0])
```

### this will take much longer to run. but its obvious that we repeat the first check for every game.
Lets rather just run that once and hard code the answer in to save a LOT of time.

The frequency model opens with 'sores' the predictive one with 'bones'. Lets determine the opener here.


```python
orange_letters_hist=[]
green_letters_hist=[]
grey_letters_hist=[]
matches = get_possible_words_old(wordsarr, orange_letters_hist, green_letters_hist, grey_letters_hist)
word_scores=[]
for word in matches:
    grey_l2 = grey_letters_hist.copy()
    orange_l = [letter[1] for letter in orange_letters_hist]
    green_l = [letter[1] for letter in green_letters_hist]
    for letter in word:
        if (letter not in green_l) and (letter not in orange_l):
            grey_l2.append(letter)
    remaining = len(get_possible_words_old(wordsarr, orange_letters_hist, green_letters_hist, grey_l2))
    word_scores.append([word, remaining])
word_scores=pd.DataFrame(word_scores)
word_scores.columns=['word', 'score']
word_scores=word_scores.sort_values(by=['score'],ascending=True)
guess=str(word_scores['word'].iloc[0])
```


```python
print(guess)
print(word_scores.head())
word_scores.to_csv('firstword.csv')
```

'toeas' is the recommended first guess it .. is a word ... feels a liiiittle like cheating, but lets go with it! This speeds things up A LOT. Lets also figure out what the next best guess is and lock that in too


```python
orange_letters_hist=[]
green_letters_hist=[]
grey_letters_hist=['t','a','o','e','s']
matches = get_possible_words(wordsarr, orange_letters_hist, green_letters_hist, grey_letters_hist)
word_scores=[]
for word in matches:
    grey_l2 = grey_letters_hist.copy()
    orange_l = [letter[1] for letter in orange_letters_hist]
    green_l = [letter[1] for letter in green_letters_hist]
    for letter in word:
        if (letter not in green_l) and (letter not in orange_l):
            grey_l2.append(letter)
    remaining = len(get_possible_words(wordsarr, orange_letters_hist, green_letters_hist, grey_l2))
    word_scores.append([word, remaining])
word_scores=pd.DataFrame(word_scores)
word_scores.columns=['word', 'score']
word_scores=word_scores.sort_values(by=['score'],ascending=True)
guess=str(word_scores['word'].iloc[0])
```


```python
print(guess)
print(word_scores.head())
word_scores.to_csv('secondword.csv')
```

"unhip" ... like me? I have to say, I'm not convinced but, hey, I'm not a computer. Lets try it out.


```python
from wordle_remaining import play_wordle_remaining
from wordle_remaining_pred import play_wordle_remaining_pred
from wordle_freq_pred import play_wordle_freq_pred
```

```python
play_wordle_freq_pred(5, wordsarr, answerlist, freq_model, False, 'smart')
```

![png](/assets/images/wordle5.PNG)
    


```python
play_wordle_remaining(5, 'toeas', 'unhip', wordsarr, answerlist, freq, False, 'smart')
```

![png](/assets/images/wordle6.PNG)
    


```python
play_wordle_remaining_pred(5, 'toeas', 'unhip', wordsarr, answerlist, freq_model, False, 'smart')
```

![png](/assets/images/wordle7.PNG)
    

## Predictive version actually got to an answer where every other try has failed on 'smart'! Lets try more examples


```python
play_wordle_freq_pred(5, wordsarr, answerlist, freq_model, False, 'helix')
```

![png](/assets/images/wordle8.PNG)
    


```python
play_wordle_remaining(5, 'toeas', 'unhip', wordsarr, answerlist, freq, False, 'helix')
```

![png](/assets/images/wordle9.PNG)
    


```python
play_wordle_remaining_pred(5, 'toeas', 'unhip', wordsarr, answerlist, freq_model, False, 'helix')
```

![png](/assets/images/wordle10.PNG)
    

#### they definitely seem to perform better than the models not looking at remaining options