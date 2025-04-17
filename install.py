# install.py
# Phase 1 & 2: Identity, Temp Email Setup, and GitHub Registration with Email Verification

import os
import time
import subprocess
import requests
import random
from faker import Faker
from pathlib import Path
from dotenv import load_dotenv, set_key
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import undetected_chromedriver as uc
import re

load_dotenv()

# Setup directories
Path(".logs").mkdir(exist_ok=True)
Path(".env").touch()

LOG_FILE = ".logs/setup.log"
ENV_FILE = ".env"

# Logger
log = open(LOG_FILE, "a", encoding="utf-8")
def write_log(msg):
    print(msg)
    try:
        log.write(f"{msg.encode('ascii', 'ignore').decode()}\n")
    except Exception as e:
        log.write(f"[Encoding Error] {str(e)}\n")

# Phase 1: Create identity and temp email
write_log("\n🚀 Starting Phase 1: Identity + Email Setup (1secmail)")
fake = Faker()
first_name = fake.first_name()
last_name = fake.last_name()
full_name = f"{first_name} {last_name}"
username = f"{first_name.lower()}.{last_name.lower()}{random.randint(100,999)}"
domain = "1secmail.com"
email_address = f"{username}@{domain}"
password = fake.password(length=12)

write_log(f"Generated identity: {full_name} / Email: {email_address}")

# No registration needed for 1secmail, just set and poll
api_base = "https://www.1secmail.com/api/v1/"

# Save to .env
set_key(ENV_FILE, "BOT_NAME", full_name)
set_key(ENV_FILE, "BOT_USERNAME", username)
set_key(ENV_FILE, "BOT_PASSWORD", password)
set_key(ENV_FILE, "BOT_EMAIL", email_address)
set_key(ENV_FILE, "EMAIL_DOMAIN", domain)

write_log("📝 Identity saved to .env")
write_log("✅ Phase 1 complete with 1secmail.")

# Phase 2: GitHub account creation using Selenium
write_log("\n🌐 Starting Phase 2: GitHub Account Creation")
options = uc.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
driver = uc.Chrome(options=options)

try:
    driver.get("https://github.com/signup")
    time.sleep(3)

    email_field = driver.find_element(By.ID, "email")
    email_field.send_keys(email_address)
    email_field.send_keys(Keys.ENTER)
    time.sleep(3)

    username_field = driver.find_element(By.ID, "login")
    username_field.send_keys(username)
    username_field.send_keys(Keys.ENTER)
    time.sleep(3)

    password_field = driver.find_element(By.ID, "password")
    password_field.send_keys(password)
    password_field.send_keys(Keys.ENTER)
    time.sleep(5)

    write_log("📨 GitHub registration form submitted. Waiting for email...")

    # Wait for GitHub email (max 90s)
    email_id = None
    for i in range(18):
        time.sleep(5)
        resp = requests.get(f"{api_base}?action=getMessages&login={username}&domain={domain}").json()
        github_emails = [m for m in resp if 'GitHub' in m['from'] or 'github' in m['from']]
        if github_emails:
            email_id = github_emails[0]['id']
            break

    if email_id:
        write_log("📧 GitHub email received. Fetching confirmation link...")

        email_data = {}
        for attempt in range(10):
            time.sleep(3)
            try:
                resp = requests.get(f"{api_base}?action=readMessage&login={username}&domain={domain}&id={email_id}")
                content_type = resp.headers.get("Content-Type", "")
                if "application/json" not in content_type:
                    write_log(f"⚠️ Unexpected content type (attempt {attempt+1}/10): {content_type}")
                    continue

                email_data = resp.json()
                if email_data.get("body") or email_data.get("htmlBody"):
                    break
                else:
                    write_log(f"⏳ Email received but empty (attempt {attempt+1}/10)...")
            except Exception as e:
                write_log(f"⏳ Exception while reading email (attempt {attempt+1}/10): {str(e)}")
        else:
            write_log("❌ Failed to get valid email content after 10 retries.")
            email_data = {}

        html_body = email_data.get("htmlBody", "") or email_data.get("body", "")
        links = re.findall(r'https://github\\.com/verify.*?["\']', html_body)
        if links:
            verification_link = links[0].rstrip('"\'')
            driver.get(verification_link)
            time.sleep(5)
            write_log("✅ GitHub email verified!")
        else:
            write_log("❌ Could not find verification link in email body.")
    else:
        write_log("❌ No GitHub verification email received in time.")

    # Save GitHub details
    set_key(ENV_FILE, "GITHUB_USERNAME", username)
    set_key(ENV_FILE, "GITHUB_PASSWORD", password)
    write_log("📝 GitHub credentials saved to .env")

except Exception as e:
    write_log(f"❌ GitHub registration failed: {str(e)}")
finally:
    driver.quit()

print("\n✅ Identity + GitHub registration complete. Ready to proceed to Netlify.")
log.close()