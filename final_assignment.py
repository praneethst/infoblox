import os
import csv
import requests
import json
import pycountry
from datetime import datetime
import pandas as pd
from statistics import mode


r = requests.get('https://lich.training.infoblox.com/transcripts.json', auth=('training', 'infoblox'))

data=r.json()
csvheaders=list(data[0].keys())
csv_writers = {}

finaldata=[]
for entry in data:
	examcode = entry['Exam Code']
	result = entry['Result']
	datecompleted = entry['Date Completed']
	starttime = entry['Start Time']
	endtime = entry['End Time']
	country_name = entry['Country']

	####Parse data - date completed
	date_obj = datetime.strptime(datecompleted, "%d %B %Y")
	formatted_date = date_obj.strftime("%Y-%m-%d")
	entry.update({'Date Completed':formatted_date})

	####Parse data - start time
	hours = starttime[:2]
	minutes = starttime[2:4]
	formatted_start_time = f"{hours}:{minutes}"
	entry.update({'Start Time':formatted_start_time})

	####Parse data - end time
	hours = endtime[:2]
	minutes = endtime[2:4]
	formatted_end_time = f"{hours}:{minutes}"
	entry.update({'End Time':formatted_end_time})

	####Parse data - 2 letter ISO country code
	try:
		country = pycountry.countries.get(name=country_name)
		if country:
			iso_code = country.alpha_2
			entry.update({'Country':iso_code})
		else:
			entry.update({'Country':country_name})
	except LookupError:
		print(f"Invalid country name: {country_name}")
	
	finaldata.append(list(entry.values()))

sorted_data = sorted(finaldata, key=lambda x: datetime.strptime(x[3], '%Y-%m-%d'))


passfile=[]
failfile=[]
for entry in sorted_data:
	examcode = entry[14]
	result = entry[2]

	if result == 'Pass':
		filename = f"{examcode}_pass_data.csv"
		csvfile = open(filename, mode='a', newline='')
		csv_writer = csv.writer(csvfile)
		if filename not in passfile:
			csv_writer.writerow(csvheaders)
			passfile.append(filename)
		#csvfile = open(filename, mode='a', newline='')
		#csv_writer = csv.writer(csvfile)
		csv_writer.writerow(entry)
	
	if result == 'Fail':
		filename = f"{examcode}_fail_data.csv"
		csvfile = open(filename, mode='a', newline='')
		csv_writer = csv.writer(csvfile)
		if filename not in failfile:
			csv_writer.writerow(csvheaders)
			failfile.append(filename)
		#csvfile = open(filename, mode='a', newline='')
		#csv_writer = csv.writer(csvfile)
		csv_writer.writerow(entry)
	



sortedpassfile=sorted(passfile)

outputdatalist=[]
for file in sortedpassfile:
	file_path = file
	examcode = file.split('_')[0]
	data = pd.read_csv(file_path)
	
	values = data['Overall Score']


	mean_value = values.mean()
	median_value = values.median()
	mode_value = mode(values)
	range_value = values.max() - values.min()
	midrange_value = (values.max() + values.min()) / 2


	outputdata = {"Exam Code" : examcode, "Mean" : mean_value, "Median" : median_value, "Mode" : mode_value, "Range" : range_value, "Midrange" : midrange_value }

	outputdatalist.append(outputdata)

df = pd.DataFrame(outputdatalist)
csv_file_path = "output.csv"
df.to_csv(csv_file_path, index=False)
print("Assginment comepleted!! - Please check the output.csv and PR0000* files generated. Thank you for the opportunity!!")
