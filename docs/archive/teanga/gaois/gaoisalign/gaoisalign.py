# brian.oraghallaigh@dcu.ie

# Requires hunalign.exe & cygwin1.dll from LF Aligner in same directory

import ast
from bs4 import BeautifulSoup
import csv
import math
import os
from pathlib import Path
import re
import regex
import requests
from requests.adapters import HTTPAdapter
import subprocess
from wtpsplit import SaT
import xml.etree.ElementTree as ET
import zipfile

# Comment out to skip sentence splitting using SaT (EU):
sat = SaT("sat-3l-sm") # Select SaT Model for sentence segmentation. See: https://github.com/segment-any-text/wtpsplit

# Funciton to decode accented character entities in source xml:
def decode_xml_fadas(text):
	text = re.sub(r'<Afada ?/>', 'Á', text)
	text = re.sub(r'<afada ?/>', 'á', text)
	text = re.sub(r'<Efada ?/>', 'É', text)
	text = re.sub(r'<efada ?/>', 'é', text)
	text = re.sub(r'<Ifada ?/>', 'Í', text)
	text = re.sub(r'<ifada ?/>', 'í', text)
	text = re.sub(r'<Ofada ?/>', 'Ó', text)
	text = re.sub(r'<ofada ?/>', 'ó', text)
	text = re.sub(r'<Ufada ?/>', 'Ú', text)
	text = re.sub(r'<ufada ?/>', 'ú', text)
	return text

# Function to replace xml special characters with xml entity references:
def clean_for_xml(segment):
	segment = segment.replace('<', '&lt;')
	segment = segment.replace('>', '&gt;')
	segment = segment.replace('&', '&amp;')
	segment = segment.replace('\'', '&apos;')
	segment = segment.replace('\"', '&quot;')
	return segment

# Function to get paragraphs of text from xml document (IE):
def xml_to_txt(data):
	data = decode_xml_fadas(data)
	soup = BeautifulSoup(data, features='xml')
	p_elements = soup.find_all('p')
	text = ''
	for p_element in p_elements:
		text = text + '\n' + p_element.get_text(separator='\n', strip=True).replace('\n', ' ')
	return text

# Function to get paragraphs of text from html document (EU):
def html_to_txt(data):
	soup = BeautifulSoup(data, features='xml')
	p_elements = soup.find_all('p')
	text = ''
	# TODO merge pars in same table row...
	for p_element in p_elements:
		text = text + '\n' + p_element.get_text(separator='\n', strip=True).replace('\n', ' ')
	return text

# Function to download large file in chunks:
def download_url(url, save_path, chunk_size=128):
	r = requests.get(url, stream=True)
	with open(save_path, 'wb') as fd:
		for chunk in r.iter_content(chunk_size=chunk_size):
			fd.write(chunk)

# Function to evaluate f-string variables within template string:
def fstr(template):
    return eval(f'f"""{template}"""')

jurisdiction = 'eu' # EDIT/CONFIGURE THIS LINE ('ie' or 'eu')
data_dir = r'C:\Users\oraghab\Documents\BOR\zzz\gaoisalign' # EDIT/CONFIGURE THIS LINE

if jurisdiction == 'ie':

	# Directories where data files will be stored locally:
	ie_ga_dir = 'ie_ga' # From Rannóg an Aistriúcháin -- Create automatically then populate MANUALLY
	ie_en_dir = 'ie_en' # From Irish Statute Book (eISB) -- Create and populate automatically
	ie_bi_dir = 'ie_bi' # For aligned data -- Create and populate automatically

	# Create above directories if they do not already exist:
	Path(data_dir).mkdir(parents=True, exist_ok=True)
	Path(os.path.join(data_dir, ie_ga_dir)).mkdir(parents=True, exist_ok=True)
	Path(os.path.join(data_dir, ie_en_dir)).mkdir(parents=True, exist_ok=True)
	Path(os.path.join(data_dir, ie_bi_dir)).mkdir(parents=True, exist_ok=True)

	input(f'\nPut the Irish-language XML files you wish to align into "{data_dir}\\{ie_ga_dir}" and press Enter...\n')

	# Prepare xml and txt files:
	print('Preparing xml and txt files...\n')

	# Create list of ie_ga xml files:
	files_ga_xml = []
	for file in os.listdir(os.path.join(data_dir, ie_ga_dir)):
		if file.endswith('.xml'):
			files_ga_xml.append(file)

	batch = []

	# For each ie_ga xml file:
	for file in files_ga_xml:
		print(file)
		file_no_extension, file_extension = os.path.splitext(file)
		file_ga_xml = os.path.join(data_dir, ie_ga_dir, file_no_extension+file_extension)
		file_ga_txt = os.path.join(data_dir, ie_ga_dir, file_no_extension+'.txt')
		file_en_xml = os.path.join(data_dir, ie_en_dir, file_no_extension+file_extension)
		file_en_txt = os.path.join(data_dir, ie_en_dir, file_no_extension+'.txt')
		
		# Generate ie_ga txt file from xml source:
		# Read xml data:
		with open(file_ga_xml, 'r', encoding='utf-8') as f:
			data = f.read()
			text_ga = ''
			text_ga = xml_to_txt(data)
		# Write txt data:
		with open(file_ga_txt, 'w', encoding='utf-8') as f:
			f.write(text_ga)

		# Get ie_en xml file from IrishStatuteBook.ie:
		act_num = str(int(file[1:3]))
		act_year = '20'+file[3:5]
		# e.g. https://www.irishstatutebook.ie/eli/2018/act/7/enacted/en/xml
		url = f'https://www.irishstatutebook.ie/eli/{act_year}/act/{act_num}/enacted/en/xml'
		x = requests.get(url)
		with open(file_en_xml, 'w', encoding='utf-8') as f:
			f.write(x.text)
		
		# Generate ie_en txt file from xml source:
		with open(file_en_txt, 'w', encoding='utf-8') as f:
			data = x.text
			text_en = ''
			text_en = xml_to_txt(data)
			f.write(text_en)
		
		# Build batch for hunalign:
		aligned_file = os.path.join(data_dir, ie_bi_dir, file_no_extension+'.tsv')
		batch.append((file_ga_txt, file_en_txt, aligned_file))

elif jurisdiction == 'eu':
	
	# Directories where data files will be stored locally:
	eu_ga_dir = 'eu_ga' # From EUR-Lex -- Create and populate automatically
	eu_en_dir = 'eu_en' # From EUR-Lex -- Create and populate automatically
	eu_bi_dir = 'eu_bi' # For aligned data -- Create and populate automatically

	# Create above directories if they do not already exist:
	Path(data_dir).mkdir(parents=True, exist_ok=True)
	Path(os.path.join(data_dir, eu_ga_dir)).mkdir(parents=True, exist_ok=True)
	Path(os.path.join(data_dir, eu_en_dir)).mkdir(parents=True, exist_ok=True)
	Path(os.path.join(data_dir, eu_bi_dir)).mkdir(parents=True, exist_ok=True)
	
	# Prepare html and txt files:
	print('Preparing html and txt files...\n')
	
	celex_list = ['32025B00331', '32025B00964R(01)', '32025R0327', '32025R1534']
	
	# Populate celex_list from EUR-Lex SOAP API if empty:
	if not celex_list:

		# Namespaces for EUR-Lex SOAP API:
		namespaces = {
			'soap': 'http://www.w3.org/2003/05/soap-envelope',
			'eurlex': 'http://eur-lex.europa.eu/search'
		}

		# URL and headers required for EUR-Lex SOAP API:
		url="https://eur-lex.europa.eu/EURLexWebService"
		headers = {
			'Accept': 'text/xml, multipart/*',
			'Content-Type': 'application/soap+xml',
			'SOAPAction': 'https://eur-lex.europa.eu/EURLexWebService/doQuery'
		}

		# Expert query for EUR-Lex SOAP API. Create account on EUR-Lex and use GUI to build query:
		expert_query = '(DTS_SUBDOM = ("LEGISLATION" OR "EFTA" OR "CONSLEG" OR "PRE_ACTS" OR "EU_CASE_LAW" OR "PAR_QUESTION" OR "LEGAL_PROCEDURE" OR "TREATIES" OR "INTER_AGREE") OR FM = ("BUDGET" OR "COMMUNIC" OR "CONCL" OR "DEC_DEL" OR "DIR_DEL" OR "REG_DEL" OR "PAPER_GREEN" OR "AGREE_INTERNATION" OR "RECO_DEC" OR "RECO_DIR" OR "RECO_REG" OR "RECO_RES" OR "PAPER_WHITE")) AND (PD >= 01/01/2025 <= 30/09/2025)'

		# Read credentials from file containing "{'usr': 'YOUR_EURLEX-USERNAME', 'pwd': 'YOUR_EURLEX-PASSWORD'}":
		with open('credentials.txt', 'r', encoding='utf-8') as data:
			credentials = ast.literal_eval(data.read())

		# Credentials for EUR-Lex SOAP API:
		usr = credentials['usr']
		pwd = credentials['pwd']

		# Envelope for EUR-Lex SOAP API:
		page = 1
		body = f"""<?xml version="1.0" encoding="UTF-8"?>
		<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope" xmlns:sear="http://eur-lex.europa.eu/search">
		  <soap:Header>
			<wsse:Security xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd" soap:mustUnderstand="true">
			  <wsse:UsernameToken xmlns:wsu="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd" wsu:Id="UsernameToken-1">
				<wsse:Username>{usr}</wsse:Username>
				<wsse:Password Type="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordText">{pwd}</wsse:Password>
			  </wsse:UsernameToken>
			</wsse:Security>
		  </soap:Header>
		  <soap:Body>
			<sear:searchRequest>
			  <sear:expertQuery><![CDATA[{expert_query}]]></sear:expertQuery>
			  <sear:page>{str(page)}</sear:page>
			  <sear:pageSize>100</sear:pageSize>
			  <sear:searchLanguage>en</sear:searchLanguage>
			  <sear:showDocumentsAvailableIn>ga</sear:showDocumentsAvailableIn>
			  <sear:excludeAllConsleg>false</sear:excludeAllConsleg>
			  <sear:limitToLatestConsleg>false</sear:limitToLatestConsleg>
			</sear:searchRequest>
		  </soap:Body>
		</soap:Envelope>"""

		# Check results are not already cached:
		if not os.path.isfile('celex_list.txt'):
			
			print('Getting celex numbers of search results...')
			
			# Make initial request to EUR-Lex SOAP API:
			response = requests.request('POST', url, headers=headers, data=body)

			# Parse response from EUR-Lex SOAP API:
			root = ET.ElementTree(ET.fromstring(response.text)).getroot()

			# Find total hits to build loop to retrieve all results:
			total_hits = root.find('./soap:Body/eurlex:searchResults/eurlex:totalhits', namespaces)

			# Calculate total pages and round up:
			total_pages = math.ceil(int(total_hits.text)/100)

			# Loop to make request for each page:
			while page <= total_pages:

				# Make request to EUR-Lex SOAP API for current page:
				response = requests.request('POST', url, headers=headers, data=fstr(body))
				root = ET.ElementTree(ET.fromstring(response.text)).getroot()
				
				# Get results from current page:
				results = root.findall('./soap:Body/eurlex:searchResults/eurlex:result', namespaces)
				
				# Get celex from each result on page and add to celex_list:
				for result in results:
					try:
						celex = result.find('eurlex:content/eurlex:NOTICE/eurlex:WORK/eurlex:ID_CELEX/eurlex:VALUE', namespaces).text
					except:
						celex = ''
					if celex:
						celex_list.append(celex)
				page += 1
			
			# Cache results to file:
			with open('celex_list.txt', 'w', encoding='utf-8') as f:
				for celex in celex_list:
					f.write(celex + '\n')

	langs = ['GA', 'EN']
	batch = []

	for celex in celex_list:
		print(celex)
		for lang in langs:
			# https://eur-lex.europa.eu/legal-content/GA/TXT/HTML/?uri=CELEX:32025R0327
			url = f'https://eur-lex.europa.eu/legal-content/{lang}/TXT/HTML/?uri=CELEX:{celex}'
			s = requests.Session()
			s.mount('https://eur-lex.europa.eu', HTTPAdapter(max_retries=5))
			x = s.get(url)
			data = x.text.replace(u'\xa0', ' ') # Replace non-breaking space character
			if lang == 'GA':
				with open(os.path.join(data_dir, eu_ga_dir, celex+'_'+lang+'.html'), 'w', encoding='utf-8') as f:
					f.write(data)
				with open(os.path.join(data_dir, eu_ga_dir, celex+'_'+lang+'.txt'), 'w', encoding='utf-8') as f:
					text_ga = ''
					text_ga = html_to_txt(data)
					if sat:
						# Split paragraphs into sentences using SaT:
						sentences_ga = sat.split(text_ga)
						for sentence_ga in sentences_ga:
							f.write(sentence_ga + '\n')
					else:
						f.write(text_ga)
			if lang == 'EN':
				with open(os.path.join(data_dir, eu_en_dir, celex+'_'+lang+'.html'), 'w', encoding='utf-8') as f:
					f.write(data)
				with open(os.path.join(data_dir, eu_en_dir, celex+'_'+lang+'.txt'), 'w', encoding='utf-8') as f:
					text_en = ''
					text_en = html_to_txt(data)
					if sat:
						# Split paragraphs into sentences using SaT:
						sentences_en = sat.split(text_en)
						for sentence_en in sentences_en:
							f.write(sentence_en + '\n')
					else:
						f.write(text_en)
		
		file_ga_txt = os.path.join(data_dir, eu_ga_dir, celex+'_GA.txt')
		file_en_txt = os.path.join(data_dir, eu_en_dir, celex+'_EN.txt')
		aligned_file = os.path.join(data_dir, eu_bi_dir, celex+'.tsv')
		batch.append((file_ga_txt, file_en_txt, aligned_file))

# Prepare xml and txt files:
print('\nPreparing alignment batch...\n')

# Write batch to file:
with open(f'batch_{jurisdiction}.txt', 'w', newline='\n', encoding='utf-8') as f:
	csv_out=csv.writer(f, delimiter='\t')
	for row in batch:
		csv_out.writerow(row)

# Convert batch file to unix format for hunalign:
with open(f'batch_{jurisdiction}.txt', 'rb') as f:
	data = f.read()
data = data.replace(b'\r\n', b'\n')
with open(f'batch_{jurisdiction}.txt', 'wb') as f:
	f.write(data)

# Build dictionary for hunalign:
print('Building dictionary...\n')

# Create directory for dictionary:
dic_dir = 'dic'
Path(os.path.join(data_dir, dic_dir)).mkdir(parents=True, exist_ok=True)

# Build path to save Pota Focal glossary (https://github.com/michmech/pota-focal-gluais):
save_path = os.path.join(data_dir, dic_dir, 'potafocal.xml')
# Check that file has not already been downloaded:
if not os.path.isfile(save_path):
	# Download glossary:
	x = requests.get('https://raw.githubusercontent.com/michmech/pota-focal-gluais/refs/heads/master/lexicon.xml')
	with open(save_path, 'w', encoding='utf-8') as f:
		f.write(x.text)

# Parse Pota Focal glossary:
import xml.etree.ElementTree as ET
potafocal_root = ET.parse(save_path).getroot() # https://github.com/michmech/pota-focal-gluais

# List of lines for new ga hunalign dic:
lines = []

# Add Pota Focal entries to list of lines for new ga hunalign dic:
for entry in potafocal_root.findall('entry'):
	try:
		ga = entry.find('src/scope/ortho')
		ga_string = ET.tostring(ga, encoding='unicode', method='text')
		en = entry.find('trg/scope/ortho')
		en_string = ET.tostring(en, encoding='unicode', method='text')
		lines.append(f'{en_string.strip()} @ {ga_string.strip()}\n')
	except:
		continue

# Download Téarma zipped txt termbase (https://www.tearma.ie/ioslodail/):
url = 'https://www.tearma.ie/ioslodail/25.04.01-tearma.ie-concepts.txt.zip'
save_path = os.path.join(data_dir, dic_dir, 'tearma.zip')
# Check that file has not already been downloaded:
if not os.path.isfile(save_path):
	download_url(url, save_path, chunk_size=128)

# Unzip Téarma termbase and save as txt:
zip = zipfile.ZipFile(os.path.join(data_dir, dic_dir, 'tearma.zip'))
file = zip.read('25.04.01-tearma.ie-concepts.txt')
with open(os.path.join(data_dir, dic_dir, 'tearma.txt'), 'wb') as f:
	f.write(file)

# Read lines from Téarma txt file:
with open(os.path.join(data_dir, dic_dir, 'tearma.txt'), 'r', encoding='utf-8') as f:
	tearma_data = f.readlines()

# Add Téarma entries to list of lines for new ga hunalign dic:
for line in tearma_data:
	en = line.split('\t')[0]
	ga = line.split('\t')[1]
	lines.append(f'{en.strip()} @ {ga.strip()}\n')

# Remove duplicates and sort:
lines_unique_sorted = sorted(list(set(lines)))

# Create new ga hunalign dic and write lines from Pota Focal glossary and Téarma termbase to it:
with open(os.path.join(data_dir, dic_dir, 'ga-en.dic'), 'w', encoding='utf-8') as f:
	for line in lines_unique_sorted:
		f.write(line)

# Align files with hunalign:
print('Aligning files...\n')

# Call hunalign on batch (See: https://github.com/danielvarga/hunalign):
cmd = fr'hunalign.exe {data_dir}\{dic_dir}\ga-en.dic -text -utf -bisent -realign -batch batch_{jurisdiction}.txt'
subprocess.run(cmd)

# Write aligned data to tmx format:
print('\nWriting aligned data to tmx format...')

# TMX markup prefix:
tmx_frame_prefix = """<?xml version="1.0" encoding="utf-16"?>
<!DOCTYPE tmx SYSTEM "tmx14.dtd">
<tmx version="1.4">

<header creationtool="gaoisalign.py" creationtoolversion="1.0" segtype="sentence" o-tmf="tsv" adminlang="ga" srclang="ga" datatype="plaintext">
	<prop type="name">{file}</prop>
</header>

<body>
"""

# TMX markup suffix:
tmx_frame_suffix = """
</body>
</tmx>
"""

# TMX translation unit markup:
tu_frame = """
<tu>
	<tuv xml:lang="ga">
		<seg>
		{ga}
		</seg>
	</tuv>
	<tuv xml:lang="en">
		<seg>
		{en}
		</seg>
	</tuv>
</tu>
"""

files = os.listdir(os.path.join(data_dir, f'{jurisdiction}_bi'))
files = [x for x in files if '.tsv' in x] # Filter filelist

for file in files:
	file_no_extension, file_extension = os.path.splitext(file)
	with open(os.path.join(data_dir, f'{jurisdiction}_bi', file), 'r', encoding='utf-8') as f:
		data = f.readlines()
	with open(os.path.join(data_dir, f'{jurisdiction}_bi', file_no_extension+'.tmx'), 'w', encoding='utf-8') as f:
		f.write(fstr(tmx_frame_prefix))
		for line in data:
			ga = clean_for_xml(line.split('\t')[0])
			en = clean_for_xml(line.split('\t')[1])
			# Filter empty and non-alpha results:
			ga_contains_text = regex.search(r'\p{L}', ga) # \p{L} matches a single code point in the category "letter".
			if ga and ga_contains_text:
				f.write(fstr(tu_frame))
		f.write(fstr(tmx_frame_suffix))
