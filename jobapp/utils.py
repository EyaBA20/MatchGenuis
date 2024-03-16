import re
import pickle
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np
from googletrans import Translator
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
translator = Translator()

blacklist = ["career", "opportunity", "work", "team", "mention", "experience", "knowledge", "skill", "ability", "company", "date", "qualification", "website", "open", "develop",
             "title", "excellent", "position", "email", "letter", "language", "post", "english", "center", "title", "salary","follow", "thank", "job", "good", "time", "great", "project", "required", "year", "month", "day",
             "form"]

def clean_text(text):
    # Remove URLs and anything starting with http or www
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'www\S+', '', text)
    
    # Lowercase the text
    text = text.lower()

    # Remove special characters and numbers
    text = re.sub('[^a-zA-Z]', ' ', text)

    # Remove multiple whitespaces
    text = re.sub(r'\s+', ' ', text)

    # Tokenize the text
    tokens = nltk.word_tokenize(text)
    
    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    filtered_tokens = [token.strip() for token in tokens if token not in stop_words]

    # Remove single-character tokens and blacklist words
    filtered_tokens = [token for token in filtered_tokens if len(token) > 2 and not any([x in token for x in blacklist])]

    # Lemmatize the tokens
    lemmatizer = WordNetLemmatizer()
    lemmatized_tokens = [lemmatizer.lemmatize(token) for token in filtered_tokens]
    
    # Change '-ing' verbs to root form
    final_tokens = [lemmatizer.lemmatize(token[:-3], pos='v') if token.endswith('ing') and lemmatizer.lemmatize(token, pos='v') != token else token for token in lemmatized_tokens]
    
    # Join the tokens back into a string
    cleaned_text = ' '.join(final_tokens)
    
    return cleaned_text

jobs = pd.read_csv("jobs2.csv")
jobs.rename(columns={"jobpost": "job_desc", "Company": "company_name", "Title": "job_title", "Location": "company_location", "OpeningDate": "post_date", "Salary": "salary"}, inplace=True, errors="ignore")
jobs.dropna(subset=["job_desc"], inplace=True)
jobs.drop_duplicates(subset=["job_desc"], inplace=True)
print(jobs.columns)

with open('vectorizer.pickle', 'rb') as handle:
    vectorizer = pickle.load(handle)

with open('lda_model.pickle', 'rb') as handle:
    lda_model = pickle.load(handle)

regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'

def check_phone(a, b):
    for k in [a, b]:
        try:
            k = k.replace(" ", "").split("216")[-1]
            if all([x.isdigit() for x in k]) and len(k) == 8:
                return k
        except:
            pass
    return ""
    
 
def check_email(a, b):
    for k in [a, b]:
        try:
            if re.fullmatch(regex, k):
                return k
        except:
            pass
    return ""


def check_empty(a, b):
    if a not in ["", [], None]:
        return "\n".join(a)
    elif b not in ["", [], None]:
        return b
    return ""


def calculate_similarity(job_description, resume):
    # Create a TF-IDF vectorizer object
    vectorizer = TfidfVectorizer(stop_words='english')
    
    # Fit and transform the job description and resume to TF-IDF matrices
    job_description_tfidf = vectorizer.fit_transform([job_description])
    resume_tfidf = vectorizer.transform([resume])
    
    # Calculate the cosine similarity between the two TF-IDF matrices
    cosine_similarity = np.dot(job_description_tfidf.toarray(), resume_tfidf.toarray().T)
    
    # Return the cosine similarity score
    return cosine_similarity[0][0]


def translate_wrap(x):
    try:
        return translator.translate(x, dest="en").text
    except:
        return x
    

def find_jobs(skills, n=10):
    skills = translate_wrap(skills)
    data = clean_text(skills)
    new_text_bow = vectorizer.transform([data])
    topic_probabilities = lda_model.transform(new_text_bow)
    resume_topic = topic_probabilities.argmax()
    resume_proba = topic_probabilities[0, resume_topic]
    l = []
    for i in range(len(jobs)):
        job_description = clean_text(jobs.job_desc.iloc[i])
        new_text_bow = vectorizer.transform([job_description])
        topic_probabilities = lda_model.transform(new_text_bow)
        job_topic = topic_probabilities.argmax()
        job_proba = topic_probabilities[0, job_topic]
        term_similarity = calculate_similarity(job_description, data)
        if (job_topic == resume_topic) and (term_similarity >= 0.3):
            l.append([i, term_similarity])
    l = [x[0] for x in sorted(l, key=lambda x: x[1], reverse=True)[:n]]
    recommended = [jobs.iloc[x].to_dict() for x in l]
    return recommended
