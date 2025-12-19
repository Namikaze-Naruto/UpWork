
import requests
from bs4 import BeautifulSoup
import csv
import re
import time
import os

BASE_URL = "https://www.dublindiocese.ie/parishes-mass-times/parishes-a-z/"
OUTPUT_PATH = os.path.join("..", "Output", "dublin_parishes.csv")
LOG_PATH = os.path.join("..", "Processing", "extraction_log.txt")

def log_message(msg):
    # Ensure log directory exists
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(msg + "\n")
    print(msg)

def clean_text(text):
    if not text:
        return ""
    return " ".join(text.split()).strip()

def get_parish_links():
    log_message(f"Fetching main directory: {BASE_URL}")
    try:
        response = requests.get(BASE_URL, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        links = []
        content_div = soup.find('div', class_='entry-content') or soup.find('div', id='content')
        
        if not content_div:
            log_message("ERROR: Could not find content div on main page.")
            return []

        for a in content_div.find_all('a', href=True):
            href = a['href']
            if '/parish/' in href and href != BASE_URL:
                if href not in links:
                    links.append(href)
        
        log_message(f"Found {len(links)} parish links.")
        return links
    except Exception as e:
        log_message(f"CRITICAL ERROR fetching directory: {e}")
        return []

def extract_details(url):
    data = {
        "Parish Name": "",
        "Church Names": "",
        "Priests": "",
        "Secretary": "",
        "Phone": "",
        "Email": "",
        "Address": "",
        "Parish URL": url
    }
    
    try:
        response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 1. Parish Name
        title = soup.find('h1')
        if title:
            data["Parish Name"] = clean_text(title.get_text())
        
        content = soup.find('div', class_='entry-content') or soup.find('div', id='content')
        if not content:
            log_message(f"WARNING: No content found for {url}")
            return data
            
        full_text = content.get_text(separator="\n")
        
        # 2. Church Names
        churches = []
        generic_headers = ["Contact", "Mass Times", "Confession", "Sacraments", "Details", "Introduction", "Team", "Church Information", "Church Address", "Accessibility"]
        
        for header in content.find_all(['h2', 'h3', 'h4']):
            text = clean_text(header.get_text())
            if not text: 
                continue
            
            is_generic = any(g.lower() == text.lower().replace(":", "").strip() for g in generic_headers)
            if is_generic:
                continue
                
            if len(text) > 3 and "parish" not in text.lower():
                 start_keywords = ["Church", "St", "Saint", "Our Lady", "Holy", "Mary", "Blessed", "Sacred Heart", "Nativity", "Immaculate"]
                 if any(k in text for k in start_keywords):
                     churches.append(text)
        
        if not churches:
            if "St" in data["Parish Name"] or "Church" in data["Parish Name"]:
                churches.append(data["Parish Name"])
        
        data["Church Names"] = " | ".join(sorted(list(set(churches)), key=len, reverse=True))

        # 3. Emails
        emails = set(re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', full_text))
        data["Email"] = " | ".join(sorted(list(emails)))

        # 4. Phones
        phones = set(re.findall(r'(?:\(?0\d{1,3}\)?[\s\-\.]?)?\d{3}[\s\-\.]?\d{4}', full_text))
        valid_phones = []
        for p in phones:
            digits = "".join(c for c in p if c.isdigit())
            if len(digits) >= 7 and not (len(digits)==4 and p.startswith("20")):
                valid_phones.append(p.strip())
        
        data["Phone"] = " | ".join(sorted(list(set(valid_phones))))

        # 5. Priests & Secretary
        priests = []
        secretary = []
        lines = full_text.split('\n')
        
        titles_to_skip = ["parish priest", "curate", "curates", "team", "moderator", "administrator", "parish chaplain", "co-parish priest", "chaplain", "priests of the parish", "priest in charge"]
        
        for line in lines:
            line_clean = clean_text(line)
            lower_line = line_clean.lower()
            if not line_clean:
                continue

            # Priests
            if any(marker in lower_line for marker in ["moderator", "co-pp", "curate", "adm", "chaplain", "parish priest", "very rev", "rev."]):
                clean_lower = lower_line.replace(":", "").strip()
                if clean_lower in titles_to_skip:
                    continue
                if len(line_clean) < 80 and not any(c.isdigit() for c in line_clean):
                    priests.append(line_clean)
            
            # Secretary
            if "secretary" in lower_line:
                 if ":" in line_clean or len(line_clean) < 50:
                     if lower_line.replace(":", "").strip() != "parish secretary":
                         secretary.append(line_clean)
        
        data["Priests"] = " | ".join(sorted(list(set(priests))))
        data["Secretary"] = " | ".join(sorted(list(set(secretary))))

        # 6. Address
        address_parts = []
        seen_address = set()
        for line in lines:
            line_clean = clean_text(line)
            if not line_clean: 
                continue
            if re.search(r'Dublin\s?\d+|Co\.?\s?(?:Dublin|Wicklow|Kildare)', line, re.IGNORECASE):
                if line_clean not in seen_address:
                    address_parts.append(line_clean)
                    seen_address.add(line_clean)
        
        data["Address"] = " | ".join(address_parts)

    except Exception as e:
        log_message(f"ERROR extracting {url}: {e}")

    return data

def main():
    if os.path.exists(OUTPUT_PATH):
        try:
            os.remove(OUTPUT_PATH)
        except:
            pass
            
    # Modify log path handling above or just rely on manual check
    if os.path.exists(LOG_PATH):
        try:
            os.remove(LOG_PATH)
        except:
            pass

    links = get_parish_links()
    
    # Ensure output dir exists
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    
    with open(OUTPUT_PATH, 'w', newline='', encoding='utf-8-sig') as csvfile:
        fieldnames = ["Parish Name", "Church Names", "Priests", "Secretary", "Phone", "Email", "Address", "Parish URL"]
        # USING COLON AS DELIMITER
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter=':')
        writer.writeheader()
        
        count = 0
        total = len(links)
        
        for url in links:
            count += 1
            if count % 10 == 0 or count == 1 or count == total:
                 print(f"[{count}/{total}] Processing {url}...")
            
            details = extract_details(url)
            writer.writerow(details)
            time.sleep(0.1)

    print(f"Extraction complete. Data saved to {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
