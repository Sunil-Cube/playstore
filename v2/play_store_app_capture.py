import argparse
import requests
import lxml.html as lh
import time
import csv
import re
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from pclasses.urls import *

parser = argparse.ArgumentParser()
parser.add_argument("job_url", nargs='*')
args = parser.parse_args()

app_capture_url = args.job_url[0]
app_cat_url = args.job_url[1]


webdriver.DesiredCapabilities.PHANTOMJS['phantomjs.page.customHeaders']=HEADER

dcap = dict(DesiredCapabilities.PHANTOMJS)
dcap['phantomjs.page.settings.userAgent'] = (HEADER.get('User-Agent'))

s_args = [
	#'--proxy-type=http'
	#'--proxy=104.196.243.100',
	'--ignore-ssl-errors=true',
	'--ssl-protocol=any',
	'--web-security=false'
]

app_capture = webdriver.PhantomJS(
	executable_path='phantomjs',
	desired_capabilities=dcap,
	service_args=s_args
)
app_capture.set_page_load_timeout(600)
app_capture.maximize_window()

# go to URL
print "Getting URL: %s" % app_capture_url,app_cat_url

r = requests.get(app_capture_url, verify=False, headers=HEADER)
status_code = r.status_code
print "Status Code: %s" % status_code

app_capture.get(app_capture_url)
time.sleep(7)

doc = lh.fromstring(app_capture.page_source)
app_name = doc.xpath('//*[@class="document-title"]/div/text()')
downloads = doc.xpath('//*[@itemprop="numDownloads"]/text()')
reviews_num = doc.xpath('//*[@class="reviews-num"]/text()')
develper = doc.xpath('//*[@class="dev-link"]/@href')
rating_value = doc.xpath('//*[@class="score"]/text()')
email_address = []
company_website_url = []
if develper:
	company_website_url = re.findall('=http://[a-zA-Z\.\-]+|=https://[a-zA-Z\.\-]+', develper[0])[0].split('=')[1]
	email_address = develper[1].split('mailto:')[1]

csv_app_open = open('Output_playstoreapp.csv', 'ab')
csv_app = csv.writer(csv_app_open, delimiter=',')
csv_app.writerows([[app_cat_url,app_name[0],email_address,company_website_url,downloads[0],reviews_num[0],rating_value[0]]])
csv_app_open.close()

app_capture.quit()

