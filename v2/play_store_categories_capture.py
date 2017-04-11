import time
import re
import os
import requests
import lxml.html as lh
import csv
import multiprocessing
import subprocess
from time import strftime
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import NoSuchElementException, ElementNotVisibleException
from pclasses.urls import *

def runIn():
	webdriver.DesiredCapabilities.PHANTOMJS['phantomjs.page.customHeaders']=HEADER
	dcap = dict(DesiredCapabilities.PHANTOMJS)
	dcap['phantomjs.page.settings.userAgent'] = (HEADER.get('User-Agent'))
	
	#'--proxy=69.38.16.164:8080',
	s_args = [
		#'--proxy-type=http'
		#'--proxy=104.196.243.100',
		'--ignore-ssl-errors=true',
		'--ssl-protocol=any',
		'--web-security=false'
	]
	
	store_categories_capture = webdriver.PhantomJS(
		executable_path='phantomjs',
		desired_capabilities=dcap,
		service_args=s_args
	)
	store_categories_capture.set_page_load_timeout(600)
	store_categories_capture.maximize_window()

	# go to URL
	app_categories = ['Recruitment','']
	csvopen = open('Output_playstoreapp.csv', 'ab')
	csv_w = csv.writer(csvopen, delimiter=',')
	csv_w.writerows([['Categories','App Name','Email Address','Company website URL','Installs','User evaluation']])
	csvopen.close()

	for app in app_categories:
		capture_url = "https://play.google.com/store/search?q="+app
		print "Getting URL: %s" % capture_url
		
		r = requests.get(capture_url, verify=False, headers=HEADER)
		status_code = r.status_code
		print "Status Code: %s" % status_code

		store_categories_capture.get(capture_url)
		time.sleep(7)

		# try:
		# 	store_categories_capture.find_element_by_xpath('//*[@class="see-more play-button small id-track-click apps id-responsive-see-more"]').click()
		# 	time.sleep(10)
		# except (ElementNotVisibleException, NoSuchElementException) as ex:
		# 	print ex

		page_source = lh.fromstring(store_categories_capture.page_source)
		doc = page_source.xpath('//*[@class="id-card-list card-list two-cards"]/div/div/a')

		job_urls = []
		for i, elt in enumerate(doc):
			if 'apps' in elt.attrib.get('href'):
			    job_urls.append({app: "https://" + get_base_url(capture_url) + elt.attrib.get('href')})

		proc_count = multiprocessing.cpu_count()
		if proc_count > 2:
			proc_count = 2

		print "Processors: %s" % proc_count
		pool = multiprocessing.Pool(processes=proc_count)
		pool.map(process_urls, job_urls, chunksize=1)
		pool.close()
	
	store_categories_capture.quit()
	
	
def process_urls(job_url):
    for categories in job_url:
        process_time = strftime("%Y-%m-%d %H:%M:%S")
        print "%s\tCapturing Job Url: %s" % (process_time, job_url[categories])
        cmd = '/home/sunils/playstore/v2/play_store_app_capture.py'
        url = "%s" % job_url[categories]
        cat= "%s" % categories
        log = open('/home/sunils/playstore/v2/process_app_urls.txt', 'a')      
        p = subprocess.Popen(['python', cmd, url, cat], stdout=log, stderr=log)
        p.wait()
        log.flush()
        log.close()
