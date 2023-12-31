# -*- coding: utf-8 -*-
import sys
from acs_lib import *

args = sys.argv
if len(args) == 2:
    input = args[1]
else:
    print("ARGS ERROR")
    quit()

# acs = ACS_CLASS()
acs = ACS_CLASS("idx-aoai-ads-001")
# acs = ACS_CLASS("idx-aoai-jp-1")

#results = acs.search_vector_query(input)
results = acs.search_query(input)

print(results)

system_message =f"""
Answer the question as truthfully as possible using the provided text below, and if you're unsure of the answer, say Sorry, 'I don't know'. You must answer in Japanese.

{results[0]['content']}

{results[1]['content']}

{results[2]['content']}
"""

print(system_message)

#print(f"TITLE: {input} \n\n{joke}\n")

