import os
import xml.etree.ElementTree as ET
import pandas as pd
from collections import defaultdict
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class PiesParser:
    def __init__(self, filepath):
        self.filepath = filepath
        self.ns = {'ns': 'http://www.autocare.org'}

    def parse(self):
        logging.info(f"Parsing PIES file: {self.filepath}")
        try:
            tree = ET.parse(self.filepath)
            root = tree.getroot()
        except Exception as e:
            logging.error(f"Error parsing {self.filepath}: {e}")
            return pd.DataFrame()

        items = []
        # Try namespace search
        pies_items = root.findall('.//ns:Item', self.ns)
        if not pies_items:
            # Fallback to no namespace
            pies_items = root.findall('.//Item')
            self.ns = None 

        for item in pies_items:
            part_data = {}
            ns = self.ns
            
            # Helper
            def get_text(path):
                n = item.find(path, ns)
                return n.text if n is not None else None
            
            # Base Fields
            part_data['PartNumber'] = get_text('ns:PartNumber' if ns else 'PartNumber') or "N/A"
            part_data['Brand'] = get_text('ns:BrandLabel' if ns else 'BrandLabel')
            
            # Descriptions - Filter for EN
            desc_tag = 'ns:Description' if ns else 'Description'
            descriptions = []
            for d in item.findall(f'.//{desc_tag}', ns):
                # Check LanguageCode attribute. namespace might apply to attribute? Usually NO. 
                # ElementTree attributes don't use namespace generally unless prefixed.
                lang = d.get('LanguageCode')
                if lang == 'EN' and d.text:
                    descriptions.append(d.text)
            
            # If no EN found, fallback to any? 
            # Ideally user wants clean data, so maybe just EN. 
            if not descriptions:
                 # Fallback: try finding descriptions without lang attribute or just take first
                 descriptions = [d.text for d in item.findall(f'.//{desc_tag}', ns) if d.text and not d.get('LanguageCode')]

            part_data['Description'] = descriptions[0] if descriptions else "" 

            # Features - Filter for EN
            feats = []
            mkt_tag = 'ns:MarketCopyContent' if ns else 'MarketCopyContent'
            for mkt in item.findall(f'.//{mkt_tag}', ns):
                if mkt.get('LanguageCode') == 'EN' and mkt.text:
                    feats.append(mkt.text)
            part_data['Features'] = " | ".join(feats)

            # Attributes - FLATTENING & filtering
            attr_tag = 'ns:ProductAttribute' if ns else 'ProductAttribute'
            for attr in item.findall(f'.//{attr_tag}', ns):
                # Filter EN
                if attr.get('LanguageCode') != 'EN':
                     continue
                     
                a_id = attr.get('AttributeID')
                val = attr.text
                if a_id and val:
                    # Clean ID for column name
                    clean_id = f"Attribute_{a_id.replace(' ', '_')}"
                    part_data[clean_id] = val
                    
            # Images
            img_tag = 'ns:DigitalFileInformation' if ns else 'DigitalFileInformation'
            fname_tag = 'ns:FileName' if ns else 'FileName'
            images = []
            for asset in item.findall(f'.//{img_tag}', ns):
                f_node = asset.find(fname_tag, ns)
                if f_node is not None and f_node.text:
                    images.append(f_node.text)
            part_data['Images'] = ";".join(images)
            
            items.append(part_data)
            
        return pd.DataFrame(items)

class AcesParser:
    def __init__(self, filepath):
        self.filepath = filepath

    def parse(self):
        logging.info(f"Parsing ACES file: {self.filepath}")
        try:
            tree = ET.parse(self.filepath)
            root = tree.getroot()
        except Exception as e:
            logging.error(f"Error parsing {self.filepath}: {e}")
            return pd.DataFrame()

        mapping = defaultdict(list)
        
        for app in root.iter('App'):
            part = app.find('Part')
            part_num = part.text if part is not None else None
            
            if not part_num:
                continue
                
            bv = app.find('BaseVehicle')
            bv_id = bv.get('id') if bv is not None else ""
            
            # If we had Year/Make model map, we'd apply it here.
            # Using ID for now as per constraints.
            if bv_id:
                mapping[part_num].append(bv_id)

        data = []
        for p, fits in mapping.items():
            # Join IDs with comma
            data.append({
                'PartNumber': p,
                'VehicleIDs': ",".join(fits[:100]) # Limit
            })
            
        return pd.DataFrame(data)

def process_directory(work_dir):
    input_dir = os.path.join(work_dir, 'Input')
    output_dir = os.path.join(work_dir, 'Output')
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    all_pies = []
    all_aces = []
    
    logging.info(f"Scanning Input: {input_dir}")
    for root_dir, dirs, files in os.walk(input_dir):
        for f in files:
            if f.lower().endswith('.xml'):
                full_path = os.path.join(root_dir, f)
                if 'pies' in f.lower():
                    df = PiesParser(full_path).parse()
                    if not df.empty:
                        all_pies.append(df)
                elif 'aces' in f.lower():
                    df = AcesParser(full_path).parse()
                    if not df.empty:
                        all_aces.append(df)

    # Merge PIES
    if all_pies:
        logging.info("Concatenating PIES data...")
        master_df = pd.concat(all_pies, ignore_index=True)
        # Drop duplicates if any
        master_df.drop_duplicates(subset=['PartNumber'], keep='last', inplace=True)
    else:
        master_df = pd.DataFrame(columns=['PartNumber'])

    # Merge ACES
    if all_aces:
        logging.info("Concatenating ACES data...")
        fitment_df = pd.concat(all_aces, ignore_index=True)
        # Aggregate logic: Group by part and join strings (if multiple rows per part)
        fitment_df = fitment_df.groupby('PartNumber')['VehicleIDs'].apply(lambda x: ",".join(x)).reset_index()
    else:
        fitment_df = pd.DataFrame(columns=['PartNumber'])

    # Final Merge
    logging.info("Merging ACES and PIES...")
    final_df = pd.merge(master_df, fitment_df, on='PartNumber', how='left')
    
    # Cleaning: Drop columns where all values are NaN or empty strings
    # Convert empty strings to NaN first
    final_df.replace("", float("nan"), inplace=True)
    before_cols = len(final_df.columns)
    final_df.dropna(axis=1, how='all', inplace=True)
    after_cols = len(final_df.columns)
    logging.info(f"Dropped {before_cols - after_cols} empty columns.")
    
    # Save CSV
    csv_path = os.path.join(output_dir, 'Consolidated_Catalog.csv')
    try:
        final_df.to_csv(csv_path, index=False)
        logging.info(f"Saved CSV to {csv_path}")
    except Exception as e:
        logging.error(f"Failed to save CSV: {e}")

    # Optional: Save Excel too if manageable
    xlsx_path = os.path.join(output_dir, 'Consolidated_Catalog.xlsx')
    try:
        # Excel has row/col limits. If columns > 16384 (unlikely with just attributes) it fails.
        # But if sparse attributes create thousands of columns? 
        # PIES attributes are usually standard.
        final_df.to_excel(xlsx_path, index=False)
        logging.info(f"Saved Excel to {xlsx_path}")
    except Exception as e:
        logging.error(f"Failed to save Excel: {e}")

if __name__ == "__main__":
    WORK_DIR = r"d:\UpWork\04_Aces_Pies_Data" 
    process_directory(WORK_DIR)
