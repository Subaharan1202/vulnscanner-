from django.shortcuts import render
from django.shortcuts import redirect
# Create your views here.
from django.http import HttpResponse


import sys
import time
import logging
import argparse
from threading import Thread
from dotenv import load_dotenv, find_dotenv


from vulpackage.scanners.zap_scanner import ZapScanner
from vulpackage.scanners.nexpose_scanner import NexposeScanner
from vulpackage.scanners.openvas_scanner import OpenVASScanner
from vulpackage.scanners.scanner import Scanner
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
                scanner.start('scan_name', 'target')
                time.sleep(1)
    return redirect(index)

def pause(request):

    for scanner in scanners:
                scanner.start_sp('scan_name')
                time.sleep(1)
    return redirect(index)

def resume(request):
    for scanner in scanners:
                scanner.resume('scan_name')
                time.sleep(1)
    return redirect(index)

def stop(request):
    for scanner in scanners:
                scanner.stop('scan_name')
                time.sleep(1)
    return redirect(index)

def remove(request):
    for scanner in scanners:
                scanner.remove('scan_name')
                time.sleep(1)
    return redirect(index)
                
def es(request):
    Scanner().enable_scanner_services()
    time.sleep(1)
    exit()
    return redirect(index)

def ds(request):
    Scanner().disable_scanner_services()
    ZapScanner().shutdown()
    time.sleep(1)
    exit()
    return redirect(index)

def list(request):
    for scanner in scanners:
                scanner.list_scans()
                time.sleep(1)
    return redirect(index)

def pss(request):
    for scanner in scanners:
                scanner.get_scan_status('scan_name', scan_status_list)

                Scanner().print_scan_status(scan_status_list)
    return redirect(index)

def spstart(request):
    for scanner in scanners:
                scanner.start_sp('scan_name')
                time.sleep(1)
    return redirect(index)
def report(request):
    for scanner in scanners:
                if scanner == scanners[0]:
                    scanner.get_scan_results('scan_name', zscan_results)
                    time.sleep(2)

                elif scanner == scanners[1]:
                    scanner.get_scan_results('scan_name', nscan_results)
                    time.sleep(2)
                elif scanner == scanners[2]:
                    scanner.get_scan_results('scan_name', oscan_results)
                    time.sleep(2)

                try:
                    if 'Report':
                        
                       res=Thread(target=Scanner().print_report(zscan_results, nscan_results, oscan_results)).start()

                        
                    if 'export':
                        
                        Thread(target=Scanner().export('scan_name', zscan_results, nscan_results,
                                                       oscan_results)).start()
                        
                except:
                    print("Error: unable to output report")
    #res=[["aa","sssddd","ddddd","ugfff","fdfjfjfj"],["hhdhhdd","dhdhdhhd","dhdgdggd","ggdggdgd","hdhdgdgdgdgd"]]                


    return render(request,'vulpackage/view.html',{"vul":res})
    