import time
import random
import string
import imaplib
import email
import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from fake_useragent import UserAgent

# Your referral link
REFERRAL_LINK = "https://klokapp.ai?referral_code=FW486LV2"

# Email settings (update accordingly)
IMAP_SERVER = "imap.gmail.com"  # Replace with your email provider
EMAIL_USER = "wakinjoseph351@gmail.com"
EMAIL_PASS = "uqpd buce cjay rnac"

# CAPTCHA solving (if required)
TWO_CAPTCHA_API_KEY = "your-2captcha-api-key"

# File containing proxies (each proxy in format: http://username:password@proxy:port)
PROXY_FILE = "proxy.txt"

# File to store created accounts
LOG_FILE = "accounts.txt"


def get_proxy():
    """Extracts one proxy per account from proxy.txt"""
    try:
        with open(PROXY_FILE, "r") as f:
            proxies = [line.strip() for line in f.readlines()]
        return random.choice(proxies) if proxies else None
    except FileNotFoundError:
        print("[ERROR] Proxy file not found. Running without proxy.")
        return None


def generate_random_email():
    """Generates a random email using temporary email domains"""
    domains = ["@gmail.com", "@yahoo.com", "@outlook.com"]
    username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    return username + random.choice(domains), username  # Return email and username


def setup_browser(proxy=None):
    """Sets up a Selenium browser with or without a proxy"""
    options = uc.ChromeOptions()
    ua = UserAgent()
    options.add_argument(f"user-agent={ua.random}")

    if proxy:
        print(f"[INFO] Using proxy: {proxy}")
        options.add_argument(f"--proxy-server={proxy}")

    # Explicitly set the Chrome binary location (Modify if needed)
    options.binary_location = "/usr/bin/google-chrome"

    driver = uc.Chrome(options=options)
    return driver


def fetch_verification_code(email_address):
    """Fetches verification code from email using IMAP"""
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL_USER, EMAIL_PASS)
        mail.select("inbox")

        status, messages = mail.search(None, f'FROM "no-reply@klokapp.ai" SUBJECT "Verification Code"')
        if messages[0]:
            for num in messages[0].split():
                status, msg_data = mail.fetch(num, "(RFC822)")
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        body = msg.get_payload(decode=True).decode()
                        verification_code = ''.join(filter(str.isdigit, body))  # Extract numbers
                        return verification_code
        return None
    except Exception as e:
        print(f"[ERROR] Fetching verification code failed: {e}")
        return None


def automate_signup(use_proxy):
    """Automates signup process for a referral system"""
    proxy = get_proxy() if use_proxy else None
    email, username = generate_random_email()

    print(f"[INFO] Creating account with email: {email}")

    driver = setup_browser(proxy)
    driver.get(REFERRAL_LINK)
    time.sleep(5)  # Wait for the page to load

    # Find and fill the email field (update selector as per the website)
    email_input = driver.find_element(By.NAME, "email")
    email_input.send_keys(email)

    # Click register or next button (update selector as needed)
    register_btn = driver.find_element(By.XPATH, '//button[@type="submit"]')
    register_btn.click()

    time.sleep(10)  # Wait for the email verification to arrive

    verification_code = fetch_verification_code(email)
    if verification_code:
        print(f"[INFO] Verification Code: {verification_code}")
        code_input = driver.find_element(By.NAME, "verification_code")
        code_input.send_keys(verification_code)
        code_input.send_keys(Keys.RETURN)
    else:
        print("[ERROR] Failed to retrieve verification code.")

    time.sleep(5)
    driver.quit()

    # Save account details
    with open(LOG_FILE, "a") as f:
        f.write(f"{email} | {'Proxy: ' + proxy if proxy else 'No Proxy'}\n")


def mass_referral_signup(num_accounts, use_proxy):
    """Runs the referral signup automation multiple times"""
    for _ in range(num_accounts):
        automate_signup(use_proxy)
        time.sleep(random.randint(10, 20))  # Random delay to avoid detection


if __name__ == "__main__":
    # Ask user whether to use a proxy or not
    use_proxy = input("Use proxy? (Y/N): ").strip().lower() == 'y'
    
    # Ask how many accounts to create
    num_accounts = int(input("Enter number of accounts to create: ").strip())

    mass_referral_signup(num_accounts, use_proxy)
