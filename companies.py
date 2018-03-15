"""
Python script to interact with companies house api.
Set up to download files from companies house
"""

import requests
import time
import json
import re
import sys
from passwords import AUTH_TOKEN
DEBUG = True
URI_BASE = 'https://api.companieshouse.gov.uk'
TOKEN = AUTH_TOKEN
RETRIES = 2
# should index be 0?
index = 1
BATCH_SIZE_DEFAULT = 10 
TOTAL_COMPANIES_DEFAULT = 40
SEARCH_DEFAULT = 'dog'
DOCUMENTS_DEFAULT = 5

array = "" 
full_details = []

def dprint(my_print_statement):
	if DEBUG:
		print(my_print_statement)
		

def apiCall(my_uri, my_search_term = None, my_number_of_items = None, my_index_offset = None):
	"""
	This calls the companies house api
	It retries up to "RETRIES" times if there is an error.
	"""
	dprint("--Starting apiCall: " + my_uri)
	error_count = 0
	try:
		if (my_search_term is not None) and (my_index_offset is not None) and (my_number_of_items is not None):
			dprint("Parameters provided")
			params = (
				('q', my_search_term),
				('items_per_page', my_number_of_items),
				('start_index', my_index_offset)
			)
			dprint("params: " + params[0][1])
		else:
			params = None

		dprint("pre loop" + str(error_count))
		while error_count < RETRIES:
			dprint("loop: " + str(error_count))
			response = requests.get(my_uri, params=params, auth=(TOKEN, ''))
			dprint("got response ")
			#print response.json()
			# Use 4 to find error responses 400, 404, etc.
			if "4" in response:
				print("Error waiting 5 min before retry")
				time.sleep( 5 * 60 + 1 )
				error_count += 1
			else:
				#good response
				dprint("Good response:")
				return response
		
		print("Error:", response)
		raise ValueError('Unable to make api call: ' + response)
	except:	
		dprint("--- API Call Error: " + sys.exc_info())


def main():
	"""

	"""
	dprint("---> Starting main")
	args = ''.join(sys.argv)
	dprint("ARGS: " + args)
	
	documents_total	= int(re.match(r'.*\-d([^\- ]*).*', args).group(1))
	
	dprint("docuents per entity: " + str(documents_total))
	
	try:
		total = int(re.match(r'.*\-n([^\- ]*).*', args).group(1))
		dprint("total: " + str(total) )
	except:
		total = TOTAL_COMPANIES_DEFAULT
		pass
	try:
		search = re.match(r'.*\-s([^\- ]*).*', args).group(1)
		dprint("search: " + search)
	except:
		search = SEARCH_DEFAULT
		pass
	
	try:
		dprint("Arguments Total: " + str(total) + " search: " + str(search))
		page_total = total / BATCH_SIZE_DEFAULT	
		for page in range(0, page_total):			
			index = page * BATCH_SIZE_DEFAULT
			response = apiCall(URI_BASE + '/search', search, BATCH_SIZE_DEFAULT, index).json()
			if page == 0: total = total if total < response['total_results'] else response['total_results']				
			companies = response['items']	
			for company in companies:
				print company['company_number']
				filing_history = apiCall(URI_BASE + '/company/'+company['company_number']+'/filing-history').json()
				print filing_history
				company_files =[company, filing_history]
				for document in filing_history['items']:
					#print document['links']['document_metadata']
					document_content = requests.get(document['links']['document_metadata']+'/content', auth=(TOKEN,''))
					#print document_content.text
					company_files.append(document_content)
					company_files.append(document_content.content)
					f = open('cache/' + company['company_number'] + '_' + document['transaction_id'], "w")
					f.write(document_content.content)
				f.close()

				full_details.append(company_files)							
					


		#print array

		file = open("cache/dogs.txt", "w")
		file.write(full_details)
		file.close()

	except:
		dprint("Error: " + response )
		pass
	finally:
		return 1

print("starting")
if __name__ == '__main__':
	main()


	

