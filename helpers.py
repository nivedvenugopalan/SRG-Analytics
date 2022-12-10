import nltk

lemmatizer = nltk.stem.WordNetLemmatizer() 
stop_words = set(nltk.corpus.stopwords.words('english')) 

def lemmatize(word):     
    lemmatizer.lemmatize(word)  

def remove_stopwords(sentence):     
    tokens = nltk.tokenize.word_tokenize(sentence)     
    filtered = [w for w in tokens if not w in stop_words]     
    return filtered  

def remove_non_alpha(sentence):     
    words = [word.lower() for word in sentence.split(" ") if word.isalpha()]
    return words