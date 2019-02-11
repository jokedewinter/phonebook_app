
from search import *


def plural_check(results):
	if len(results) > 1:
		plural = 's'
	else:
		plural = ''

	return plural


def get_business_results(category, name, location):
	if category and category != "Business Type":
		results = search_business_type(category.title(), location)
	elif name:
		results = search_business_name(name.title(), location)
	else:
		results = search_business_name("", location)

	return results
