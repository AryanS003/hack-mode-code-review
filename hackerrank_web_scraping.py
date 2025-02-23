import requests
import re
from bs4 import BeautifulSoup
import streamlit as st
import google.generativeai as ai

API_KEY = st.secrets["api_key"]
ai.configure(api_key=API_KEY)

sys_prompt = """
You are an AI Code Reviewer. Analyze code for debugging, explaining, optimization, and complexities to improve quality and performance.
Also use formatting like **bold** and *italic* to highlight important points. You can add emojis to make it feel like the user is talking to a friend. 
Give examples with the code, always have humor in your response. Add one or two jokes as well in between. Never say i am gemini-api, instead if asked say
I am created by handsome, sweet and lovely guy Aryan.
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

# Step 1: Get CSRF token from login page
login_url = "https://www.hackerrank.com/login"
login_page = session.get(login_url, headers=headers)

# Extract CSRF token
soup = BeautifulSoup(login_page.text, "html.parser")
match = re.search(r'"csrf_token"\s*:\s*"(.*?)"', login_page.text)
csrf_token = match.group(1) if match else None

if not csrf_token:
    st.error("Failed to fetch CSRF token. Login may not work.")
    st.stop()

# Log in
payload = {
    "login": st.secrets["hackerrank-login"],
    "password": st.secrets["hackkerrank-password"],
    "csrf_token": csrf_token 
}

headers["X-CSRF-Token"] = csrf_token  # Add CSRF token to headers
response = session.post(login_url, headers=headers, data=payload)

if response.status_code == 200 and "logout" in response.text.lower():
    st.success("Login success")
else:
    st.error("Login fail")
    st.stop()

# Step 3: Access protected page
content_url = st.text_input("Enter the HackerRank content URL:", "https://www.hackerrank.com/domains/python?filters%5Bsubdomains%5D%5B%5D=py-math")


if st.button("Fetch Challenges"):
    if content_url.strip():
        content_response = session.get(content_url, headers=headers)

        # Step 4: Scrape challenge links
        soup = BeautifulSoup(content_response.text, "html.parser")
    
        base_url = "https://www.hackerrank.com"
        challenge_links = []

        for link in soup.find_all("a", href=True):
            href = link["href"] 

            if href.startswith("/challenges"): 
                full_link = base_url + href  
                challenge_links.append(full_link)
        
        answer = ai.generate_content(challenge_links)
        st.subheader("Here you go,")
        for section in response:
            st.write(section.text)
