import requests
import re
from bs4 import BeautifulSoup
import streamlit as st
import google.generativeai as ai

API_KEY = st.secrets["api-key"]
ai.configure(api_key=API_KEY)


sys_prompt = """
You are an AI Coder. write code, explain code in details and complexities in short.
Use **bold**, *italic*, and emojis to make responses engaging. Add humor and jokes in between. 
Never say "I am Gemini-API"; instead, say "I am created by a handsome, sweet, and lovely guy, Aryan."
"""

gemini = ai.GenerativeModel(model_name="models/gemini-2.0-flash-exp", system_instruction=sys_prompt)

session = requests.Session()
login_url = "https://www.hackerrank.com/login"

# define headers
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://www.hackerrank.com/",
    "Accept-Language": "en-US,en;q=0.9",
}

# define payload
payload = {
    "login": st.secrets["hackerrank-login"],  # Fixed typo
    "password": st.secrets["hackerrank-password"]
}

response = session.post(login_url, headers=headers, data=payload)

# extracting csrf_token from response.text
key_val_text = response.text
pattern = r'"csrf_token"\s*:\s*"(.*?)"'
match = re.search(pattern, key_val_text)

if match:
    csrf_token = match.group(1)
else:
    st.warning("csrf_token not found")

login_page = session.get(login_url, headers=headers)

# Add CSRF token to headers and payload
payload["csrf-token"] = csrf_token
headers["X-CSRF-Token"] = csrf_token  

response = session.post(login_url, headers=headers, data=payload)

# login check
if response.status_code == 200:
    st.success("Yo! I'm free, give me a hackerrank challenge link and see the magic! 😎")
else:
    st.error("Login fail")
    st.stop()

# user input url
content_url = st.text_input("Enter the HackerRank URL:", placeholder = "https://www.hackerrank.com/domains/python?filters%5Bsubdomains%5D%5B%5D=py-math")

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
            st.write("challenges scraped: ", formatted_links)
            for section in answer.parts:
                st.write(section.text)
        else:
            st.warning("No challenges found on the provided page.")
