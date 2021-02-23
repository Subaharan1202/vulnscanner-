from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse


import sys
import time
import logging
import argparse
from threading import Thread
from dotenv import load_dotenv, find_dotenv

from scanners.zap_scanner import ZapScanner
from scanners.nexpose_scanner import NexposeScanner
from scanners.openvas_scanner import OpenVASScanner
from scanners.scanner import Scanner
load_dotenv(find_dotenv())
import os

logging.basicConfig(filename='vuln-scanner.log', level=logging.INFO)

scanners = [ZapScanner(), NexposeScanner(),OpenVASScanner()]

zscan_results = {}
nscan_results = {}
oscan_results = {}
scan_status_list = []




def index(request):
    return render(request,'vulpackage/index.html',{'id':3})



def start(request):
	for scanner in scanners:
                scanner.start(config['scan_name'], config['target'])
                time.sleep(1)

def pause():

	for scanner in scanners:
                scanner.start_sp(config['scan_name'])
                time.sleep(1)

def  resume():
	 for scanner in scanners:
                scanner.resume(config['scan_name'])
                time.sleep(1)

def stop():
	for scanner in scanners:
                scanner.stop(config['scan_name'])
                time.sleep(1)

def remove():
	for scanner in scanners:
                scanner.remove(config['scan_name'])
                time.sleep(1)

def es():
	Scanner().enable_scanner_services(config)
    time.sleep(1)
    exit()
def ds():
    Scanner().disable_scanner_services(config)
    ZapScanner().shutdown()
    time.sleep(1)
    exit()
def list():
	for scanner in scanners:
                scanner.list_scans()
                time.sleep(1)


def pss():
	for scanner in scanners:
                scanner.get_scan_status(config.get('scan_name'), scan_status_list)

                Scanner().print_scan_status(scan_status_list)
def  report():
	for scanner in scanners:
                   if scanner == scanners[0]:
                       scanner.get_scan_results(config.get('scan_name'), zscan_results)
                       time.sleep(2)

                   elif scanner == scanners[1]:
                        scanner.get_scan_results(config.get('scan_name'), nscan_results)
                        time.sleep(2)
                   elif scanner == scanners[2]:
                        scanner.get_scan_results(config.get('scan_name'), oscan_results)
                        time.sleep(2)

                try:
                    if config['Report']:
                        
                        Thread(target=Scanner().print_report(zscan_results, nscan_results, oscan_results)).start()
                        
                    if config['export']:
                        
                        Thread(target=Scanner().export(config.get('scan_name'), zscan_results, nscan_results,
                                                       oscan_results)).start()
                        
                except:
                    print("Error: unable to output report")
	