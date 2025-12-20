import os
import xml.etree.ElementTree as ET
import pandas as pd
from collections import defaultdict
import glob
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
        # Handle Namespace: Check if root has it. If not, use wildcard or empty.
        # The sample showed <PIES xmlns="..."> so we use namespace.
        # But to be robust, we can use wildcard tag searches usually, but ElementTree is strict.
        # We will try with namespace first.
        
        # Helper to find text safely
        def find_text(elem, path, namespaces=None):
            node = elem.find(path, namespaces)
            return node.text if node is not None else ""

        # Find all Items
        # Try namespace search
        pies_items = root.findall('.//ns:Item', self.ns)
        if not pies_items:
            # Fallback to no namespace if finding fails (e.g. if xmlns is different or stripped)
            pies_items = root.findall('.//Item')
            self.ns = None 

        for item in pies_items:
            part_data = {}
            ns = self.ns
            
            # Base Fields
            part_data['PartNumber'] = find_text(item, 'ns:PartNumber' if ns else 'PartNumber', ns) or "N/A"
            part_data['Brand'] = find_text(item, 'ns:BrandLabel' if ns else 'BrandLabel', ns)
            
            # Descriptions
            desc_tag = 'ns:Description' if ns else 'Description'
            descriptions = [d.text for d in item.findall(f'.//{desc_tag}', ns) if d.text]
            part_data['Description'] = " | ".join(descriptions)
            
            # Attributes
            attr_tag = 'ns:ProductAttribute' if ns else 'ProductAttribute'
            attributes = []
            for attr in item.findall(f'.//{attr_tag}', ns):
                a_id = attr.get('AttributeID') or "Attr"
                val = attr.text
                if val:
                    attributes.append(f"{a_id}: {val}")
            part_data['Attributes'] = " | ".join(attributes)
            
            # Images
            img_tag = 'ns:DigitalFileInformation' if ns else 'DigitalFileInformation'
            fname_tag = 'ns:FileName' if ns else 'FileName'
            images = []
            for asset in item.findall(f'.//{img_tag}', ns):
                f_node = asset.find(fname_tag, ns)
                if f_node is not None and f_node.text:
                    images.append(f_node.text)
            part_data['Images'] = " | ".join(images)
            
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
        
        # ACES Structure: <App><BaseVehicle id="..."/><Part>...</Part></App>
        # Iterate all App elements safely
        for app in root.iter('App'):
            # Part
            part = app.find('Part')
            part_num = part.text if part is not None else None
            
            if not part_num:
                continue
                
            # Base Vehicle
            bv = app.find('BaseVehicle')
            bv_id = bv.get('id') if bv is not None else ""
            
            # Note
            note = app.find('Note')
            note_text = note.text if note is not None else ""
            
            compat_str = f"VehicleID:{bv_id}"
            if note_text:
                compat_str += f" ({note_text})"
                
            if bv_id: # Only add if we have at least a vehicle ID
                mapping[part_num].append(compat_str)

        data = []
        for p, fits in mapping.items():
            data.append({
                'PartNumber': p,
                'Compatibility': " || ".join(fits[:50]) + ("..." if len(fits) > 50 else "") # Limit to avoid Excel limits
            })
            
        return pd.DataFrame(data)

def process_directory(base_dir, output_file):
    all_pies = []
    all_aces = []
    
    # Walk directory to find all XMLs
    for root_dir, dirs, files in os.walk(base_dir):
        for f in files:
            if f.lower().endswith('.xml'):
                full_path = os.path.join(root_dir, f)
                
                # Heuristic to identify file type
                if 'pies' in f.lower():
                    df = PiesParser(full_path).parse()
                    if not df.empty:
                        all_pies.append(df)
                elif 'aces' in f.lower():
                    df = AcesParser(full_path).parse()
                    if not df.empty:
                        all_aces.append(df)

    # Master Data (PIES)
    if all_pies:
        master_df = pd.concat(all_pies, ignore_index=True)
        master_df.drop_duplicates(subset=['PartNumber'], inplace=True)
    else:
        logging.warning("No PIES data found!")
        master_df = pd.DataFrame(columns=['PartNumber'])

    # Fitment Data (ACES)
    if all_aces:
        fitment_df = pd.concat(all_aces, ignore_index=True)
        # Aggregate Fitment
        # Note: If we have multiple ACES files for same part, we concatenate the fitment strings
        # This simple logic assumes fitment strings are unique-ish or just piles them up
        # Ideally we group by PartNumber and join unique strings
        fitment_df = fitment_df.groupby('PartNumber')['Compatibility'].apply(lambda x: " || ".join(x)).reset_index()
    else:
        logging.warning("No ACES data found!")
        fitment_df = pd.DataFrame(columns=['PartNumber'])

    # Merge
    final_df = pd.merge(master_df, fitment_df, on='PartNumber', how='left')
    
    # Save
    logging.info(f"Saving {len(final_df)} rows to {output_file}...")
    final_df.to_excel(output_file, index=False)
    logging.info("Success.")

if __name__ == "__main__":
    # Adjust valid paths as per user environment
    BASE_PATH = r"d:\UpWork\04_Aces_Pies_Data" 
    OUT_PATH = os.path.join(BASE_PATH, "Consolidated_Data.xlsx")
    process_directory(BASE_PATH, OUT_PATH)
