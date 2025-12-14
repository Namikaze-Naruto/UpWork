import re
import csv

INPUT_FILE = r"d:\UpWork\data.txt"
OUTPUT_FILE = r"d:\UpWork\extracted_data.csv"
# START_LINE = 491  <-- User requested whole file
# END_LINE = 3591

def extract_data():
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        all_lines = f.readlines()

    # subset for processing
    # Process ALL lines
    subset = all_lines
    
    extracted_records = []

    # Regex patterns
    # Matches "Priority creditor's name" or "Nonpriority creditor's name"
    header_pattern = re.compile(r'(Priority|Nonpriority)\s+creditor\'s\s+name', re.IGNORECASE)
    
    # Amount pattern: $xx,xxx.xx
    amount_pattern = re.compile(r'\$(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)')
    
    # City State Zip pattern
    # Columbus, OH 43216
    # Duluth, MN 55802
    csz_pattern = re.compile(r'^(.*),\s+([A-Z]{2})\s+(\d{5}(?:-\d{4})?)')
    
    # Split Name / Address 1 pattern
    split_pattern = re.compile(r'^(.*?)\s+((?:P\.?O\.?\s*Box.*|\d+\s+[A-Z].*))$', re.IGNORECASE)

    i = 0
    while i < len(subset):
        line = subset[i]
        stripped = line.strip()
        
        # 1. Search for header
        if header_pattern.search(line):
            # Extract Amount
            amt_match = amount_pattern.findall(line)
            amount = amt_match[-1] if amt_match else "0.00"
            
            # 2. Search for Address Block (First Quoted Block)
            address_lines = []
            found_block = False
            
            # Look ahead
            j = i + 1
            while j < len(subset):
                # Safety break: if we've looked too far ahead (e.g. 15 lines), 
                # assume this header is malformed or done.
                if j - i > 15:
                    break
                    
                sub_line = subset[j].strip()
                
                # Check if we hit another header -> Stop looking for address
                if header_pattern.search(subset[j]):
                    # We missed the address for the previous record?
                    # Or maybe there wasn't one.
                    # Backtrack i so the outer loop handles this new header
                    i = j - 1
                    break
                
                if not found_block:
                    if sub_line.startswith('"'):
                         # Potential block start. Check content to see if it's a Record ID (e.g. "3.104")
                        content_check = sub_line[1:]
                        # If it's a short block starting with digit+dot, likely a record ID.
                        # Heuristic: starts with \d+\.
                        if re.match(r'^\d+\.', content_check):
                            # Skip this block (Record ID)
                            if '"' in content_check:
                                pass
                            else:
                                while j < len(subset) - 1:
                                    j += 1
                                    if '"' in subset[j]:
                                        break
                            continue
                        
                        # Heuristic: Checkboxes
                        if '□' in content_check or '■' in content_check or 'Check all that apply' in content_check:
                             # Skip this block (Form metadata)
                            if '"' in content_check:
                                pass
                            else:
                                while j < len(subset) - 1:
                                    j += 1
                                    if '"' in subset[j]:
                                        break
                            continue
                        
                        found_block = True
                        # Parse this block
                        # The block starts with ".
                        # We need to find the ending ".
                        
                        # Handle content on start line
                        # remove leading quote
                        content = sub_line[1:]
                        
                        # Check for closing quote in content
                        # Note: content might handle multiple quotes? 
                        # We assume the address block is the first quoted string.
                        # It ends at the first unescaped quote? (CSV style rules? or just simple quote)
                        # Based on file, it seems simply "Start ... End"
                        
                        if '"' in content:
                            # Ends on same line
                            end_idx = content.find('"')
                            address_lines.append(content[:end_idx])
                            # Block done
                            process_record(extracted_records, address_lines, amount, csz_pattern, split_pattern)
                            # Advance i to j
                            i = j
                            break
                        else:
                            # Start of multi-line block
                            address_lines.append(content)
                            # Continues to next lines...
                
                else:
                    # Inside block
                    if '"' in sub_line:
                        # Found closing quote
                        end_idx = sub_line.find('"')
                        address_lines.append(sub_line[:end_idx])
                        # Block done
                        process_record(extracted_records, address_lines, amount, csz_pattern, split_pattern)
                        # Advance i to j
                        i = j
                        break
                    else:
                        address_lines.append(sub_line)
                
                j += 1
            
            # If we exhausted j without finding block or finishing block, i will be updated by outer loop
            if not found_block:
                 # Should we warn?
                 pass
            else:
                 # If we finished block (break called), i is set to j.
                 # If we hit `break` due to new header, i is set to j-1.
                 pass

        i += 1

    # Write to CSV
    headers = ["Name", "Address 1", "Address 2", "City", "State", "Zip", "Amount"]
    
    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(extracted_records)
        
    print(f"Extraction complete. Found {len(extracted_records)} records.")

def process_record(records, lines, amount, csz_regex, split_regex):
    if not lines:
        return

    # Filter out junk lines (Date, Last 4 digits) that might be captured in Nonpriority blocks
    # Strategy: Find the line matching CSZ. Discard everything after.
    
    valid_lines = []
    city = ""
    state = ""
    zip_code = ""
    
    csz_index = -1
    
    # Scan from bottom up? Or top down?
    # CSZ is usually near the end.
    for idx, l in enumerate(lines):
        # Clean line
        l_clean = l.strip()
        match = csz_regex.search(l_clean)
        if match:
            city = match.group(1).strip()
            state = match.group(2).strip()
            zip_code = match.group(3).strip()
            csz_index = idx
            # We assume the first match we find (or last?) is the valid one.
            # Usually address block has only one CSZ line.
            # But "Date" line implies we should stop there.
            # "Date" line won't match CSZ.
            break # Found it.
    
    if csz_index != -1:
        # valid lines are 0 to csz_index-1
        valid_lines = lines[:csz_index]
    else:
        # No CSZ found. Treat all lines as address.
        # But wait, if we have "Date(s)..." at end, we should remove them.
        # Heuristic: Remove lines starting with "Date" or "Last 4 digits".
        cleaned = []
        for l in lines:
            if l.strip().startswith("Date") or l.strip().startswith("Last 4"):
                break
            cleaned.append(l)
        valid_lines = cleaned

    if not valid_lines and csz_index == -1:
        # Weird empty case
        return

    # Name and Addr 1 split
    name = ""
    addr1 = ""
    addr2 = ""
    
    if valid_lines:
        first_line = valid_lines[0].strip()
        match_split = split_regex.match(first_line)
        if match_split:
            name = match_split.group(1).strip()
            addr1 = match_split.group(2).strip()
        else:
            name = first_line
        
        # Remaining valid lines are Addr2
        middle = valid_lines[1:]
        if middle:
            combined = " ".join([m.strip() for m in middle])
            if addr1:
                addr2 = combined
            else:
                addr1 = combined
    else:
        # Only CSZ line existed?
        name = "UNKNOWN" 

    records.append({
        "Name": name,
        "Address 1": addr1,
        "Address 2": addr2,
        "City": city,
        "State": state,
        "Zip": zip_code,
        "Amount": amount
    })

if __name__ == '__main__':
    extract_data()
