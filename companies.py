import requests
import time
import json
from passwords import AUTH_TOKEN
TOKEN = AUTH_TOKEN
index = 1
items = 10 
total = 1000
array = "" 
full_details = []
for i in range(0,2):
	index = i * items
	params = (
		('q', 'dog'),
		('items_per_page', items),
		('start_index', index)
	)
	response = requests.get('https://api.companieshouse.gov.uk/search', params=params, auth=(TOKEN, ''))

	if "4" in response:
		time.sleep( 5*60 )
		print("Error")
	else:
		array=array +response.text
		jsoncomp=response.json()
		companies = jsoncomp['items']
		
		for company in companies:
			print company['company_number']
			filing_history = requests.get('https://api.companieshouse.gov.uk/company/'+company['company_number']+'/filing-history', auth=(TOKEN,'')).json()
			print filing_history
			company_files =[company, filing_history]
			for document in filing_history['items']:
				#print document['links']['document_metadata']
				document_content = requests.get(document['links']['document_metadata']+'/content', auth=(TOKEN,''))
				#print document_content.text
				company_files.append(document_content)
				company_files.append(document_content.content)
				f = open(company['company_number'] + document['transaction_id'], "w")
				f.write(document_content.content)
			f.close()

			full_details.append(company_files)							
				


#print array

file = open("dogs.txt", "w")
file.write(full_details)
file.close()


exit
	

