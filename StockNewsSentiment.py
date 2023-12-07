
# Author: Sam Sullivan
# STOCK SENTIMENT ANALYSIS USING NEWSAPI

import requests
from textblob import TextBlob
from collections import Counter
import spacy
import tkinter as tk
from tkinter import ttk, Text, Scrollbar
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import webbrowser 

chart_canvas = None  

def create_open_link_function(url):
    return lambda event: webbrowser.open(url)

nlp = spacy.load("en_core_web_sm")

API_KEY = '83b637f89d7e4bddac643c0cd1d6d9c7'

# Function to fetch articles from NewsAPI
def fetch_articles(query, pagesize=100): 
    endpoint = 'https://newsapi.org/v2/everything'

    params = {
        'apiKey': API_KEY,
        'q': query,
        'pageSize': pagesize,
        'language': 'en',
        'sortBy': 'publishedAt',
    }
    response = requests.get(endpoint, params=params) 
    
    if response.status_code != 200:
        results.insert(tk.END, f"Error fetching articles: {response.text}\n")
        return []
    
    return response.json().get('articles', []) 

# Function to analyze articles
def analyze_articles(articles):
    mentions = Counter() 
    stock_articles = [] 

    for article in articles: 
        content = article.get('content', '') 
        blob = TextBlob(content) 
        sentiment = blob.sentiment.polarity * 10  
        article['sentiment'] = sentiment  
        stock_articles.append(article) 
        doc = nlp(content) 
        for ent in doc.ents: 
            if ent.label_ == "ORG": 
                mentions[ent.text] += 1  
 
    return mentions, stock_articles 


    print("Analyzed Articles", stock_articles) # Debugging
    return mentions, stock_articles 

# Function to display results in GUI
def display_results(mentions, stock_articles):
    global chart_canvas  

    results.delete('1.0', tk.END)  
    if chart_canvas is not None:
        chart_canvas.get_tk_widget().destroy()
        chart_canvas = None  

    stock_ticker = stock_var.get().upper()  
    results.insert(tk.END, f"Stock Ticker: {stock_ticker}\n")  

    if stock_ticker in stock_articles and isinstance(stock_articles[stock_ticker], list):
        articles = stock_articles[stock_ticker]
        link_counter = 0  

        for article in articles:
            title = article.get('title', 'No Title')
            sentiment = article.get('sentiment', 'No Sentiment')
            article_url = article.get('url', '')

            link_tag = f"link{link_counter}"  
            link_counter += 1

            results.insert(tk.END, f"Title: ")
            results.insert(tk.END, title, link_tag)
            results.insert(tk.END, f"\nSentiment: {sentiment}\n\n")

            results.tag_bind(link_tag, "<Button-1>", create_open_link_function(article_url))

        avg_sentiments = [article['sentiment'] for article in articles if 'sentiment' in article]
        article_titles = [article['title'] for article in articles if 'title' in article]

        if avg_sentiments and article_titles:
            plt.figure(figsize=(10, 4))
            plt.bar(article_titles, avg_sentiments, color='blue')
            plt.xticks(rotation=90)
            plt.xlabel('Articles')
            plt.ylabel('Sentiment (-10 to +10)')
            plt.title(f'Sentiment Trends for {stock_ticker}')
            plt.tight_layout()

            chart_canvas = FigureCanvasTkAgg(plt.gcf(), master=root)
            canvas_widget = chart_canvas.get_tk_widget()
            canvas_widget.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
    else:
        results.insert(tk.END, "Invalid data structure for stock_articles.\n")

# Main function to fetch and analyze articles based on stock ticker
def fetch_and_analyze():
    results.delete(1.0, tk.END)  
    selected_stock = stock_var.get().upper() 

    if not selected_stock: 
        results.insert(tk.END, "Please enter a valid stock ticker.\n") 
        return 

    query = selected_stock  
    articles = fetch_articles(query) 
    if not articles: 
        results.insert(tk.END, "No articles fetched. Exiting analysis.\n") 
        return

    mentions, stock_articles = analyze_articles(articles) 
    display_results(mentions, {selected_stock: stock_articles}) 


# GUI using tkinter
root = tk.Tk() 
root.title("Stock News Analysis") 
stock_label = tk.Label(root, text="Enter Stock Ticker:") 
stock_label.pack(pady=10) 
stock_var = tk.StringVar()  
stock_entry = ttk.Entry(root, textvariable=stock_var) 
stock_entry.pack(pady=10) 
fetch_button = tk.Button(root, text="Fetch & Analyze News", command=fetch_and_analyze) 
fetch_button.pack(pady=20) 
results = Text(root, wrap=tk.WORD, height=30, width=100) 
results = Text(root, wrap=tk.WORD, height=30, width=100)
scrollbar = Scrollbar(root, command=results.yview)  
results['yscrollcommand'] = scrollbar.set
results.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
root.mainloop() 