import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

def google_search(query):
    search_url = f"https://www.google.com/search?q={query}&hl=en"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive"
    }
    response = requests.get(search_url, headers=headers)
    if response.status_code == 200:
        return response.text
    else:
        st.error("Failed to retrieve search results")
        return None

def determine_result_type(link):
    if link.endswith('.pdf'):
        return 'pdf'
    elif 'youtube.com/watch' in link or 'youtu.be/' in link:
        return 'video'
    else:
        return 'url'

def parse_results(html):
    soup = BeautifulSoup(html, "html.parser")
    results = []

    for g in soup.find_all('div', class_='tF2Cxc'):
        title = g.find('h3')
        link_tag = g.find('a')
        description_tag = g.find('div', class_='VwiC3b')
        if title and link_tag and description_tag:
            title_text = title.get_text()
            link = link_tag['href']
            description = description_tag.get_text()
            result_type = determine_result_type(link)
            results.append({"Title": title_text, "Link": link, "Description": description, "Type": result_type})

    # Additional parsing for PDF links directly in the result snippets
    for pdf in soup.find_all('a', href=True):
        link = pdf['href']
        if link.endswith('.pdf'):
            results.append({"Title": link.split('/')[-1], "Link": link, "Description": "", "Type": "pdf"})

    return results

def make_clickable(link):
    return f'<a href="{link}" target="_blank">{link}</a>'

def main():
    st.title("Google Search Streamlit App")

    query = st.text_input("Enter search query:")
    if st.button("Search"):
        if query:
            query = query + " (filetype:pdf OR site:youtube.com)"  # Extend the query to include PDFs and videos
            html = google_search(query)
            if html:
                results = parse_results(html)
                if results:
                    df = pd.DataFrame(results)
                    df.index = df.index + 1  # Start index from 1 instead of 0
                    df.reset_index(inplace=True)
                    df.rename(columns={'index': 'Sl No'}, inplace=True)
                    df['Link'] = df['Link'].apply(make_clickable)
                    df = df[['Sl No', 'Type', 'Title', 'Description', 'Link']]  # Reorder columns
                    
                    # Use st.markdown to render the DataFrame as HTML
                    st.markdown(df.to_html(escape=False, index=False), unsafe_allow_html=True)
                else:
                    st.write("No results found")
        else:
            st.write("Please enter a search query")

if __name__ == "__main__":
    main()
