#!/usr/bin/env python3

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


class Main:

    def main(self, config):

        if not (config['enable_serviceslw'] or config['enable_servicesrw'] or config['enable_servicesll'] or config[
            'enable_servicesrl'] or config['disable_serviceslw'] or config['disable_servicesrw'] or config[
                    'disable_servicesll'] or config['disable_servicesrl']):
            scanners = [ZapScanner(), NexposeScanner(),OpenVASScanner()]
        else:
            pass


        zscan_results = {}
        nscan_results = {}
        oscan_results = {}
        scan_status_list = []

        if config['target']:
            print("target")
            for scanner in scanners:
                scanner.start(config['scan_name'], config['target'])
                time.sleep(1)

        elif config['pause']:
            for scanner in scanners:
                scanner.pause(config['scan_name'])
                time.sleep(1)
        elif config['start_sp']:
            for scanner in scanners:
                scanner.start_sp(config['scan_name'])
                time.sleep(1)

        elif config['resume']:
            for scanner in scanners:
                scanner.resume(config['scan_name'])
                time.sleep(1)

        elif config['stop']:
            for scanner in scanners:
                scanner.stop(config['scan_name'])
                time.sleep(1)
        elif config['Remove']:
            for scanner in scanners:
                scanner.remove(config['scan_name'])
                time.sleep(1)
        elif config['enable_serviceslw'] or config['enable_servicesrw'] or config['enable_servicesll'] or config['enable_servicesrl']:
            Scanner().enable_scanner_services(config)
            time.sleep(1)
            exit()
        elif config['disable_serviceslw'] or config['disable_servicesrw'] or config['disable_servicesll'] or config[
            'disable_servicesrl']:
            Scanner().disable_scanner_services(config)
            ZapScanner().shutdown()
            time.sleep(1)
            exit()
        elif config['list']:
            
            for scanner in scanners:
                scanner.list_scans()
                time.sleep(1)
            
        else:
            if config['scan_status'] or config['Report'] or config['target'] :
                
                for scanner in scanners:
                    scanner.get_scan_status(config.get('scan_name'), scan_status_list)

                Scanner().print_scan_status(scan_status_list)
               

            if config['Report'] or config['export']:
                # if scan_status_list[2]['status']== 'complete (100%)':
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

        return True


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-eslw', '--enable-serviceslw', action='store_true',
                        help='Enable zap,GVM,Nexpose services on local windows ')
    parser.add_argument('-esrw', '--enable-servicesrw', action='store_true',
                        help='Enable zap,GVM,Nexpose services on  remote windows')
    parser.add_argument('-dslw', '--disable-serviceslw', action='store_true',
                        help='Disable zap,GVM,Nexpose services on  local windows')
    parser.add_argument('-dsrw', '--disable-servicesrw', action='store_true',
                        help='Disable zap,GVM,Nexpose services on remote windows')

    parser.add_argument('-esll', '--enable-servicesll', action='store_true',
                        help='Enable zap,GVM,Nexpose services on local linux ')
    parser.add_argument('-esrl', '--enable-servicesrl', action='store_true',
                        help='Enable zap,GVM,Nexpose services on remote linux ')
    parser.add_argument('-dsll', '--disable-servicesll', action='store_true',
                        help='Disable zap,GVM,Nexpose services on local linux')
    parser.add_argument('-dsrl', '--disable-servicesrl', action='store_true',
                        help='Disable zap,GVM,Nexpose services on remote linux')

    parser.add_argument('-s', '--scan-name', help='Specify a scan name')
    parser.add_argument('-L', '--list', action='store_true', help='list scans')
    parser.add_argument('-ss', '--scan-status', action='store_true', help='Print the scan status for  a scan name')
    parser.add_argument('-R', '--Report', action='store_true', help='Print Report  for a specified scan')
    parser.add_argument('-xls', '--export', action='store_true', help='Export to an excel file')
    parser.add_argument('-i', '--scan-id', help='Specify the scan id', type=int)
    parser.add_argument('-t', '--target', help='Specify the Target URL or IP')
    parser.add_argument('-p', '--pause', action='store_true', help='Pause a specified scan')
    parser.add_argument('-r', '--resume', action='store_true', help='Resume a specified scan')
    parser.add_argument('-S', '--stop', action='store_true', help='stop a specified scan')
    parser.add_argument('-st', '--start_sp', action='store_true', help='start a stopped scan')
    parser.add_argument('-Re', '--Remove', action='store_true', help='stop a specified scan')
    parser.add_argument('-v', '--version', action='version', version='VulnScanner 1.0')
    args = parser.parse_args()

    config = {
        'enable_serviceslw': args.enable_serviceslw,
        'enable_servicesrw': args.enable_servicesrw,
        'disable_serviceslw': args.disable_serviceslw,
        'disable_servicesrw': args.disable_servicesrw,
        'enable_servicesll': args.enable_servicesll,
        'disable_servicesll': args.disable_servicesll,
        'enable_servicesrl': args.enable_servicesrl,
        'disable_servicesrl': args.disable_servicesrl,
        'scan_name': args.scan_name,
        'target': args.target,
        'pause': args.pause,
        'resume': args.resume,
        'stop': args.stop,
        'export': args.export,
        'scan_status': args.scan_status,
        'Report': args.Report,
        'list': args.list,
        'Remove': args.Remove,
        'start_sp': args.start_sp
    }

    Main().main(config)

    exit(0)
