"""
Python script to interact with companies house api.
Set up to download files from companies house
"""

import requests
import time
import json
from passwords import AUTH_TOKEN

URI_BASE = 'https://api.companieshouse.gov.uk'
TOKEN = AUTH_TOKEN
RETRIES = 2
# should index be 0?
index = 1
batch_size = 10 
total = 40
page_total = total / batch_size
array = "" 
full_details = []

def apiGet(uri, search_term = None, number_of_items = None, index_offset = None):
	"""
	This calls the companies house api
	It retries up to "RETRIES" times if there is an error.
	"""
	error_count = 0
	if (search_term is not None) or (number_of_items is not None) or (index_offset is not None):
		params = (
			('q', search_term),
			('items_per_page', batch_size),
			('start_index', index_offset)
		)
	while error_count < RETRIES:

		response = requests.get(uri, params=params, auth=(TOKEN, ''))

		if "4" in response:
			print("Error waiting 5 min before retry")
			time.sleep( 5*60 )
			error_count += 1
		else:
			#good response
			return response.json()
	
	raise ValueError('Unable to make api call: ' + response)
	#don#t actually want program to continue should quit
	#return response


for page in range(0,page_total):
	index = page * batch_size
	
	params = (
		('q', 'dog'),
		('items_per_page', batch_size),
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
	

