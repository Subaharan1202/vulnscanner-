import os
import sys
import time

from pprint import pprint
from zapv2 import ZAPv2
from dotenv import load_dotenv, find_dotenv

from .scanner import Scanner
from vulpackage.core.storage_service import StorageService
from vulpackage.core.common_service import CommonService
import json

load_dotenv(find_dotenv())

API_KEY = os.getenv('ZAP_API_KEY')
SLEEP_INTERVAL = 2

proxy = json.loads(os.getenv('Lproxy'))


class ZapScanner(Scanner):
    name = 'ZAP'

    RISK_SEVERITY_MAP = {
        'Low': 2.0,
        'Medium': 5.49,
        'High': 8.5
    }

    def __init__(self):
        self.zap = ZAPv2(apikey=API_KEY, proxies=proxy)
        self.storage_service = StorageService()
        self.common_service = CommonService()

    def start(self, scan_name, target):
        print(f'[{self.name}] Starting Scan for Target: {target}')

        try:
            return self.scan(scan_name, target)
        except:
            print(f'[{self.name}] Not able to connect to the {self.name}: ', sys.exc_info())
            return False

    def pause(self, scan_name):
        if not self.is_valid_scan(scan_name):
            return False

        scan = self.storage_service.get_by_name(scan_name)
        self.zap.spider.pause(scan['ZAP']['zap_id'])
        print(f'[{self.name}] Spider Scan Paused')
        self.zap.ascan.pause(scan['ZAP']['active_scan_id'])
        print(f'[{self.name}] Active Scan Paused')
        scan['ZAP']['scan_status'] = {'status': 'PAUSED'}
        self.storage_service.update_by_name(scan_name, scan)
        return scan

    def resume(self, scan_name):
        if not self.is_valid_scan(scan_name):
            return False

        scan = self.storage_service.get_by_name(scan_name)
        self.zap.spider.resume(scan['ZAP']['zap_id'])
        print(f'[{self.name}] Spider Scan Resumed')
        self.zap.ascan.resume(scan['ZAP']['active_scan_id'])
        print(f'[{self.name}] Active Scan Resumed')

        scan['ZAP']['scan_status'] = {'status': 'Resumed'}
        self.storage_service.update_by_name(scan_name, scan)
        return scan

    def stop(self, scan_name):
        if not self.is_valid_scan(scan_name):
            return False

        scan = self.storage_service.get_by_name(scan_name)
        self.zap.spider.stop(scan['ZAP']['zap_id'])
        print(f'[{self.name}] Spider Scan Stopped')
        self.zap.ascan.stop(scan['ZAP']['active_scan_id'])
        print(f'[{self.name}] Active Scan Stopped')

        scan['ZAP']['scan_status'] = {'status': 'STOPPED'}
        self.storage_service.update_by_name(scan_name, scan)

        return scan

    def remove(self, scan_name):
        if not self.is_valid_scan(scan_name):
            return False

        scan = self.storage_service.get_by_name(scan_name)
        target = scan['target']
        #self.zap.core.deleteSiteNode(url=target)
        print(f'[{self.name}] Site [{target}] Removed')
        return scan['scan_id']

    def scan(self, scan_name, target):

        self.zap.core.set_mode('attack')
        print(f'[{self.name}] Starting Scan: {scan_name}')

        self.zap.urlopen(target)
        time.sleep(SLEEP_INTERVAL)

        scan_id = self.zap.spider.scan(target)
        scan_id = int(scan_id)
        print(f'[{self.name}] Scan Started: {scan_id}')
        time.sleep(SLEEP_INTERVAL)
        while (int(self.zap.spider.status(scan_id)) < 100):
            print(f'[{self.name}] spider scan progression: {int(self.zap.spider.status(scan_id))}% ', end='\r')

        # self.zap.ascan.enable_all_scanners()
        active_scan_id = self.zap.ascan.scan(target)
        # a_scan_id = self.zap.ascan.scan(target, recurse=True, inscopeonly=None, scanpolicyname=None, method=None, postdata=True)

        scan_data = self.storage_service.get_by_name(scan_name)

        if not scan_data:
            scan_data = {
                'scan_name': scan_name,
                'scan_id': '',
                'target': target,
                'status': ''
            }
            self.storage_service.add(scan_data)

        scan_data['ZAP'] = {
            'zap_id': scan_id,
            'active_scan_id': active_scan_id,
            'scan_status': {
                'status': 'INPROGRESS'
            }
        }
        self.storage_service.update_by_name(scan_name, scan_data)

        return scan_data

    def get_scan_status(self, scan_name, scan_status_list=[]):

        if not self.is_valid_scan(scan_name):
            return False

        scan_data = self.storage_service.get_by_name(scan_name)
        scan_status = scan_data.get('ZAP', {}).get('scan_status', {})
        zap_id = scan_data.get('ZAP', {})['zap_id']
        active_scan_id = scan_data.get('ZAP', {})['active_scan_id']
        target = scan_data['target']

        print(f'[{self.name}] Getting Scan Status for Target: {target}')
        print(f'[{self.name}] Scan Name: {scan_name}')
        print(f'[{self.name}] Scan Id: {zap_id}')

        spider_scan_status = self.zap.spider.status(zap_id)
        passive_scan_records_pending = self.zap.pscan.records_to_scan
        active_scan_status = self.zap.ascan.status(active_scan_id)

        scan_status['spider_scan'] = self._parse_status(spider_scan_status)
        scan_status['active_scan'] = self._parse_status(active_scan_status)
        scan_status['passive_scan'] = {
            'scan_pending': int(passive_scan_records_pending),
            'status': 'COMPLETE' if int(passive_scan_records_pending) == 0 else 'INPROGRESS'
        }

        scan_data['ZAP']['scan_status'] = scan_status

        self.storage_service.update_by_name(scan_name, scan_data)

        for scan_type in ['spider_scan', 'passive_scan', 'active_scan']:
            scan_type_data = scan_status.get(scan_type)
            if scan_type_data:
                scan_status_list.append({
                    'scanner': f'{self.name} ({scan_type})',
                    'status': f'{scan_type_data["status"]} ({scan_type_data.get("progress")})'
                })

        return scan_status_list

    def get_scan_results(self, scan_name, zscan_results={}):

        if not self.is_valid_scan(scan_name):
            return False

        scan_data = self.storage_service.get_by_name(scan_name)

        target = scan_data['target']

        alerts = self.zap.core.alerts(baseurl=target)
        # print (f'Alerts: {len(alerts)}')

        self._process_alerts(alerts, zscan_results)

        return zscan_results

    def _parse_status(self, status):
        if status == 'does_not_exist':
            progress = 0
            status = 'NOT_STARTED'
        else:
            progress = int(status)
            status = 'COMPLETE' if progress == 100 else 'INPROGRESS'

        data = {
            'progress': f'{progress}%',
            'status': status
        }
        return data

    def list_scans(self):
        # scans = self.zap.ascan.scans()
          print("Available scan names from ZAP")
        # print(f'[{self.name}] Scans:', len(scans))
          print(f'[{self.name}] Scans:', "suba125")   
          pass

    def is_valid_scan(self, scan_name):

        scan_data = self.storage_service.get_by_name(scan_name)
        if not scan_data:
            print(f'[{self.name}] Invalid Scan Name: {scan_name}')
            return False

        if not scan_data.get('ZAP'):
            print(f'[{self.name}] No Scan Details found for {scan_name}')
            return False

        zap_id = scan_data['ZAP']['zap_id']

        try:
            ascan_status = self.zap.ascan.status(zap_id)
        except:
            print(f'[{self.name}] Could not get the scan {zap_id}: ', sys.exc_info())
            return False

        if (ascan_status == 'does_not_exist'):
            print(f'[{self.name}] No Scans found for Scan Id {zap_id}')
            return False

        return True

    def _process_alerts(self, alerts, zscan_results):

        for alert in alerts:
            name = alert['name']
            if zscan_results.get(name) is None:
                alert['reported_by'] = self.name
                alert['urls'] = set([alert['url']])
                alert['severity'] = self.RISK_SEVERITY_MAP.get(alert['risk'])
                zscan_results[name] = alert
            else:
                zscan_results[name]['urls'].add(alert['url'])

        return zscan_results

    def start_sp(self, scan_name):
        if not self.is_valid_scan(scan_name):
            return False

        scan_data = self.storage_service.get_by_name(scan_name)
        target = scan_data['target']
        print(f'[{self.name}] Starting Scan: {scan_name}')

        self.zap.urlopen(target)
        time.sleep(SLEEP_INTERVAL)

        scan_id = self.zap.spider.scan(target)
        scan_id = int(scan_id)
        print(f'[{self.name}] Scan Started: {scan_id}')
        time.sleep(SLEEP_INTERVAL)

        # self.zap.ascan.enable_all_scanners()
        active_scan_id = self.zap.ascan.scan(target)
        # a_scan_id = self.zap.ascan.scan(target, recurse=True, inscopeonly=None, scanpolicyname=None, method=None, postdata=True)

        scan_data = self.storage_service.get_by_name(scan_name)

        scan_data['ZAP'] = {
            'zap_id': scan_id,
            'active_scan_id': active_scan_id,
            'scan_status': {
                'status': 'INPROGRESS'
            }
        }
        self.storage_service.update_by_name(scan_name, scan_data)

    def shutdown(self):
        re=self.zap.core.shutdown()
        print(re)

