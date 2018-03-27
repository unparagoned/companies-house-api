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
BATCH_SIZE_DEFAULT = 100
TOTAL_COMPANIES_DEFAULT = 40
SEARCH_DEFAULT = 'dog'
DOCUMENTS_DEFAULT = 5
content_types = [ 	'application/pdf', 
					'application/json',
					'application/xml',
					'application/xhtml+xml',
					'text/csv'
				]

summary_lists = []
def xstr(s):
	return '' if s is None else str(s)

def dprint(my_print_statement, my_print_object = None):
	if DEBUG:
		print str(my_print_statement) + xstr(my_print_object)
		
def apiCall(my_uri, my_number_of_items = None, my_index_offset = None, my_search_term = None, my_content_type = None):
	"""
	This calls the companies house api
	It retries up to "RETRIES" times if there is an error.
	"""
	dprint("---> Starting apiCall: " + my_uri)
	error_count = 0
	try:
		headers = {}
		params_list = []
		if my_search_term is not None:
			params_list.append( ('q', my_search_term) )
		if my_index_offset is not None:
			params_list.append( ('start_index', my_index_offset) )
		if my_number_of_items is not None:
			params_list.append( ('items_per_page', my_number_of_items) )
		params = tuple(params_list)		
		dprint("params: " + str(params))
		if my_content_type is not None:
			headers = { 'Accept': str(my_content_type) }

		while error_count < RETRIES:
			if error_count > 0:  dprint("Retries : " + str(error_count))
			dprint("headers: " + str(headers))
			response = requests.get(my_uri, params=params, headers = headers, auth=(TOKEN, ''))
			dprint("got response ", response)
			# Use 4 toos=ko find error responses 400, 404, etc.
			if response.status_code == 429:
				print("Error waiting 5 min before retry")
				time.sleep( 5 * 60 + 1 )
				error_count += 1
			elif response.status_code == 200:
				dprint("Good response:")
				return response
			else:
				dprint("--- Unknown status code", response.status_code)
				return response
		
		print("Error:", response)
		raise ValueError('Unable to make api call: ' + response)
	except:	
		dprint("--- API Call Error: " + sys.exc_info())


def main():
	"""

	"""
	dprint("---> Starting main")
	full_details = []
	args = ''.join(sys.argv)
	dprint("ARGS: " + args)
	try:	
		documents_total	= int(re.match(r'.*\-d([^\- ]*).*', args).group(1))
	except:
		documents_total = DOCUMENTS_DEFAULT
	dprint("docuents per entity: " + str(documents_total))
	
	try:
		companies_total = int(re.match(r'.*\-c([^\- ]*).*', args).group(1))
		dprint("total: " + str(total) )
	except:
	        companies_total = TOTAL_COMPANIES_DEFAULT	
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
		# taking negative of the negative rounded down gives rounded up value. // rounds down
		page_total = -(-companies_total // BATCH_SIZE_DEFAULT)	
		for page in range(0, page_total):			
			index = page * BATCH_SIZE_DEFAULT
			response = apiCall(URI_BASE + '/search', BATCH_SIZE_DEFAULT, index, search).json()
			dprint("Item: " + str(page) + " of total: " + str(page_total))
			dprint(response)
			if page == 0: total = total if total < response['total_results'] else response['total_results']				
			search_results = response['items']	
			#dprint(search_results)
			for search_hit in search_results:				
				#dprint(search_results)
				#search results are across companies, persons, etc. So break if result is not the kind company.
				if 'company' not in search_hit['kind']: break
				company = search_hit
				dprint("COMPANY" + str(company['company_number']))
				filing_index = 0
				filing_pages = 1
				filing_history =  apiCall(URI_BASE + '/company/' + company['company_number'] + '/filing-history', BATCH_SIZE_DEFAULT, 0).json()
				filing_pages = -(-filing_history['total_count'] // filing_history['items_per_page'])
				for filing_page in range(0, filing_pages):
					dprint(filing_history)
					company_files = [company, filing_history]
					filing_index = filing_page * BATCH_SIZE_DEFAULT
					filing_history = apiCall(URI_BASE + '/company/' + company['company_number'] + '/filing-history', BATCH_SIZE_DEFAULT, filing_index).json()
					full_details.append(company_files)	
					for document_index, document in enumerate(filing_history['items']):
						dprint("document index: " + str(document_index) + "filing index: " + str(filing_history['start_index']) + "total: " + str(documents_total))
						if ( document_index + int(filing_history['start_index']) ) < documents_total:
							dprint("SUM: " + str(document_index + int(filing_history['start_index'])))
							if 'document_metadata' in document['links']:
								document_metadata = apiCall(document['links']['document_metadata']).json()
								dprint(document_metadata)
								if 'resources' in document_metadata:
									dprint("resources are :" + str(document_metadata['resources']))
									for content_type in document_metadata['resources']:
										dprint("content: " + str(content_type))
										document_extension = re.match(r'.*/([a-z]*).*', str(content_type)).group(1)
										date_source = document_metadata['significant_date'] if document_metadata['significant_date'] is not None else document_metadata['created_at']
										document_date = re.match(r'([0-9\-]+)[^0-9\-]+.*', str(date_source)).group(1)
										dprint(" Date sig: " + str(document_metadata['significant_date']) + " created : " + str(document_metadata['created_at']) + " source: " + date_source + "doc dateL " + document_date)
										# get metadata if resources in 
										# if application/pdf or application/xhtml+xml in,
										# then send an accept content-type to the /context for the different types
										document_name = company['company_number'] + '_' + document_metadata['category'] + '_' + document_date + '.' + document_extension
										dprint("document name : " + str(document_name))
										document_content = apiCall(document['links']['document_metadata']+'/content', None, None, None, content_type)
										#document_content = apiCall(document['links']['document_metadata']+'/content')
										dprint(document_content)
										#dprint(document_content.content)
										f = open('cache/' + document_name, "w")
										f.write(document_content.content)
										f.close()
						else: break
					
											

		file = open("cache/dogs.txt", "w")
		file.write(full_details)
		file.close()

	except:
		dprint("---> Error (Main): ", sys.exc_info() ) 

		print sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2] 
		
		pass
	finally:
		return 0

print("starting")
if __name__ == '__main__':
	main()
