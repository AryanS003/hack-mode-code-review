import requests
import re
from bs4 import BeautifulSoup
import streamlit as st
import google.generativeai as ai

API_KEY = st.secrets["api-key"]
ai.configure(api_key=API_KEY)


sys_prompt = """
You are an AI Code Reviewer. Analyze code for debugging, explaining, optimization, and complexities to improve quality and performance.
Use **bold**, *italic*, and emojis to make responses engaging. Add humor and jokes in between. 
Never say "I am Gemini-API"; instead, say "I am created by a handsome, sweet, and lovely guy, Aryan."
"""

gemini = ai.GenerativeModel(model_name="models/gemini-2.0-flash-exp", system_instruction=sys_prompt)

# Define headers
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://www.hackerrank.com/",
    "Accept-Language": "en-US,en;q=0.9",
}

# Initialize session
session = requests.Session()

# Getting CSRF token from login page
login_url = "https://www.hackerrank.com/login"
login_page = session.get(login_url, headers=headers)

# Extract CSRF token
soup = BeautifulSoup(login_page.text, "html.parser")
match = re.search(r'"csrf_token"\s*:\s*"(.*?)"', login_page.text)
csrf_token = match.group(1) if match else None

if not csrf_token:
    st.error("Failed to fetch CSRF token. Login may not work.")
    st.stop()

# Logging in
payload = {
    "login": st.secrets["hackerrank-login"],  # Fixed typo
    "password": st.secrets["hackerrank-password"],  # Fixed typo
    "csrf_token": csrf_token  
}

headers["X-CSRF-Token"] = csrf_token  # Add CSRF token to headers
response = session.post(login_url, headers=headers, data=payload)

# Improved login check
if response.status_code == 200:
    st.success("Login success")
else:
    st.error("Login fail")
    st.stop()

# user input url
content_url = st.text_input("Enter the HackerRank content URL:", "https://www.hackerrank.com/domains/python?filters%5Bsubdomains%5D%5B%5D=py-math")

if st.button("Fetch Challenges"):
    if content_url.strip():
        content_response = session.get(content_url, headers=headers)

        # scrape challenge links
        soup = BeautifulSoup(content_response.text, "html.parser")
    
        base_url = "https://www.hackerrank.com"
        challenge_links = []

        for link in soup.find_all("a", href=True):
            href = link["href"] 
            if href.startswith("/challenges"): 
                challenge_links.append(base_url + href)  

        if challenge_links:
            # Convert list to formatted string
            formatted_links = "\n".join(challenge_links)
            
            answer = gemini.generate_content(formatted_links)

            st.subheader("Here you go,")
            for section in answer.parts:
                st.write(section.text)
        else:
            st.warning("No challenges found on the provided page.")
