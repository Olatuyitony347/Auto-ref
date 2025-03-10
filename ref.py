import random
import string
import time
import requests
import imaplib
import email
import json
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from fake_useragent import UserAgent
from twocaptcha import TwoCaptcha
import os

# ---- CONFIGURATIONS ----
REFERRAL_LINK = "https://crypto-project.com/ref?code=YOURCODE"
EMAIL_DOMAIN = "your-email-provider.com"
IMAP_SERVER = "imap.your-email-provider.com"
IMAP_PORT = 993
EMAIL_USER = "your-email@your-email-provider.com"
EMAIL_PASS = "your-email-password"
CAPTCHA_API_KEY = "YOUR_2CAPTCHA_API_KEY"
PROXY_FILE = "proxy.txt"
USED_PROXIES = set()  # Track used proxies

# Initialize CAPTCHA solver
solver = TwoCaptcha(CAPTCHA_API_KEY)

# Load proxies from file
def load_proxies():
    if not os.path.exists(PROXY_FILE):
        print(f"Proxy file {PROXY_FILE} not found!")
        return []

    with open(PROXY_FILE, "r") as file:
        proxies = [line.strip() for line in file if line.strip()]
    
    return proxies

PROXY_LIST = load_proxies()

# Generate random email and password
def generate_random_email():
    username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    return f"{username}@{EMAIL_DOMAIN}"

def generate_random_password():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=12))

# Function to fetch verification code using IMAP
def get_verification_code():
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
        mail.login(EMAIL_USER, EMAIL_PASS)
        mail.select("inbox")
        
        # Search for latest verification email
        result, data = mail.search(None, 'ALL')
        email_ids = data[0].split()
        
        if not email_ids:
            print("No verification emails found.")
            return None

        latest_email_id = email_ids[-1]
        result, msg_data = mail.fetch(latest_email_id, "(RFC822)")
        
        raw_email = msg_data[0][1]
        msg = email.message_from_bytes(raw_email)

        # Extract verification code from email body
        if msg.is_multipart():
            for part in msg.get_payload():
                if part.get_content_type() == "text/plain":
                    email_text = part.get_payload(decode=True).decode()
                    break
        else:
            email_text = msg.get_payload(decode=True).decode()

        print("Email content:", email_text)

        # Extract 6-digit code (adjust regex as needed)
        import re
        code_match = re.search(r'\b\d{6}\b', email_text)
        if code_match:
            return code_match.group(0)

        return None
    except Exception as e:
        print("IMAP error:", e)
        return None

# Solve CAPTCHA
def solve_captcha(captcha_url):
    try:
        result = solver.normal(captcha_url)
        return result["code"]
    except Exception as e:
        print("CAPTCHA solving error:", e)
        return None

# Get a unique proxy for each account
def get_unique_proxy():
    available_proxies = list(set(PROXY_LIST) - USED_PROXIES)
    if not available_proxies:
        print("No more unique proxies available!")
        return None
    proxy = random.choice(available_proxies)
    USED_PROXIES.add(proxy)
    return proxy

# Set up Selenium with a unique proxy and random user-agent
def setup_browser(proxy):
    options = uc.ChromeOptions()
    ua = UserAgent()
    options.add_argument(f"user-agent={ua.random}")
    options.add_argument(f"--proxy-server={proxy}")

    driver = uc.Chrome(options=options)
    return driver

# Automate referral sign-up
def automate_signup():
    email = generate_random_email()
    password = generate_random_password()
    
    proxy = get_unique_proxy()
    if not proxy:
        print("No available proxies. Stopping process.")
        return

    driver = setup_browser(proxy)
    driver.get(REFERRAL_LINK)
    time.sleep(random.uniform(2, 5))  # Mimic human delay

    # Fill in signup form
    driver.find_element(By.NAME, "email").send_keys(email)
    driver.find_element(By.NAME, "password").send_keys(password)
    driver.find_element(By.NAME, "confirm_password").send_keys(password)

    # Solve CAPTCHA if exists
    captcha_element = driver.find_element(By.ID, "captcha_image")
    captcha_url = captcha_element.get_attribute("src")
    captcha_code = solve_captcha(captcha_url)
    
    if captcha_code:
        driver.find_element(By.NAME, "captcha").send_keys(captcha_code)

    driver.find_element(By.NAME, "submit").click()
    time.sleep(3)

    # Fetch verification code
    verification_code = None
    for _ in range(10):  # Retry fetching for a minute
        verification_code = get_verification_code()
        if verification_code:
            break
        time.sleep(6)

    if verification_code:
        driver.find_element(By.NAME, "verification_code").send_keys(verification_code)
        driver.find_element(By.NAME, "verify").click()
        print(f"Referral registered: {email} using proxy {proxy}")
    else:
        print(f"Failed to verify email for {email}.")

    driver.quit()

# Mass referral farming loop with one proxy per account
def mass_referral_signup(number_of_accounts=5):
    for _ in range(number_of_accounts):
        automate_signup()
        time.sleep(random.uniform(10, 30))  # Random delay between signups

# Start farming referrals
mass_referral_signup(10)  # Adjust the number of accounts to create
