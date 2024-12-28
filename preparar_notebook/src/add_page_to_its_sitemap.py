from pathlib import Path
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom

def add_page_to_its_sitemap_from_metadata(metadata, notebook_path):
    debug = False

    title_es = metadata[0]
    title_en = metadata[1]
    title_pt = metadata[2]
    end_url = metadata[3]
    description_es = metadata[4]
    description_en = metadata[5]
    description_pt = metadata[6]
    keywords_es = metadata[7]
    keywords_en = metadata[8]
    keywords_pt = metadata[9]
    image = metadata[10]
    image_hover_path = metadata[11]
    width = metadata[12]
    height = metadata[13]
    image_extension = metadata[14]
    date = metadata[15]

    if debug: print(f"Notebook path: {notebook_path}")

    # xml file path
    xml_file_path = Path(notebook_path).parent.parent / "portfolio" / "public"
    if "posts" in str(notebook_path).lower():
        xml_file_path = xml_file_path / "sitemap_posts.xml"
    elif "tips" in str(notebook_path).lower():
        xml_file_path = xml_file_path / "sitemap_tips.xml"
    else: 
        print(f"Unknown notebook path: {notebook_path}")
        exit(1)
    if debug: print(f"XML file path: {xml_file_path}")

    # Register the namespaces
    ET.register_namespace('', "http://www.sitemaps.org/schemas/sitemap/0.9")
    ET.register_namespace('xhtml', "http://www.w3.org/1999/xhtml")

    # Read the xml file
    tree = ET.parse(xml_file_path)
    root = tree.getroot()
    if debug: print(f"XML file data: {root}")

    # Create new URL entries for each language version
    # Spanish version
    url_es = ET.SubElement(root, "url")
    loc_es = ET.SubElement(url_es, "loc")
    loc_es.text = f"https://maximofn.com/{end_url}"
    link_en = ET.SubElement(url_es, "{http://www.w3.org/1999/xhtml}link")
    link_en.set("rel", "alternate")
    link_en.set("hreflang", "en")
    link_en.set("href", f"https://maximofn.com/en/{end_url}")
    link_pt = ET.SubElement(url_es, "{http://www.w3.org/1999/xhtml}link")
    link_pt.set("rel", "alternate")
    link_pt.set("hreflang", "pt-br")
    link_pt.set("href", f"https://maximofn.com/pt-br/{end_url}")

    # English version
    url_en = ET.SubElement(root, "url")
    loc_en = ET.SubElement(url_en, "loc")
    loc_en.text = f"https://maximofn.com/en/{end_url}"
    link_es = ET.SubElement(url_en, "{http://www.w3.org/1999/xhtml}link")
    link_es.set("rel", "alternate")
    link_es.set("hreflang", "es")
    link_es.set("href", f"https://maximofn.com/{end_url}")
    link_pt = ET.SubElement(url_en, "{http://www.w3.org/1999/xhtml}link")
    link_pt.set("rel", "alternate")
    link_pt.set("hreflang", "pt-br")
    link_pt.set("href", f"https://maximofn.com/pt-br/{end_url}")

    # Portuguese version
    url_pt = ET.SubElement(root, "url")
    loc_pt = ET.SubElement(url_pt, "loc")
    loc_pt.text = f"https://maximofn.com/pt-br/{end_url}"
    link_es = ET.SubElement(url_pt, "{http://www.w3.org/1999/xhtml}link")
    link_es.set("rel", "alternate")
    link_es.set("hreflang", "es")
    link_es.set("href", f"https://maximofn.com/{end_url}")
    link_en = ET.SubElement(url_pt, "{http://www.w3.org/1999/xhtml}link")
    link_en.set("rel", "alternate")
    link_en.set("hreflang", "en")
    link_en.set("href", f"https://maximofn.com/en/{end_url}")

    # Convert the ElementTree to a string with proper formatting
    xmlstr = minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")
    
    # Remove extra blank lines while keeping the structure
    xmlstr = '\n'.join([line for line in xmlstr.split('\n') if line.strip()])

    # Remove the XML declaration from minidom and add our own
    xmlstr = xmlstr.replace('<?xml version="1.0" ?>\n', '')
    xmlstr = '<?xml version="1.0" encoding="UTF-8"?>\n' + xmlstr

    # Write the formatted XML to file
    with open(xml_file_path, 'w', encoding='UTF-8') as f:
        f.write(xmlstr)
