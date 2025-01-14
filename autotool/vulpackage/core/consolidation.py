from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())
from vulpackage.core.common_service import CommonService
import os
class Consolidation:

 def __init__(self):
     self.common_service = CommonService()


 def consolidation(self, zscan_report, nscan_report, oscan_report,dup):

    self.unique_nexpose = []
    self.unique_openvas = []
    self.new_zap = zscan_report[:]



    for i in range(len(nscan_report)):
        for j in range(len(self.new_zap)):
            name_nexpose = nscan_report[i][1]
            name_zap = self.new_zap[j][1]

            p = self.common_service.is_duplicate(name_nexpose, name_zap)

            if p >= float(os.getenv('DUPLICATE_MATCH_PERCENTAGE_THRESHOLD')):
                dup.append(nscan_report[i])
                break
            elif j == int(len(self.new_zap)) - 1:
                self.unique_nexpose.append(nscan_report[i])
            else:
                continue

    self.new_zap.extend(self.unique_nexpose)



    for i in range(len(oscan_report)):
        for j in range(len(self.new_zap)):
            name_openvas = oscan_report[i][1]
            name_zap_nexpose = self.new_zap[j][1]

            cve_openvas = oscan_report[i][4]
            cve_zap_nexpose = self.new_zap[j][4]

            if cve_openvas == cve_zap_nexpose and len(cve_openvas ) >5:
                dup.append(oscan_report[i])
                break
            else:
                p = self.common_service.is_duplicate( name_openvas, name_zap_nexpose)
                if p >= float(os.getenv('DUPLICATE_MATCH_PERCENTAGE_THRESHOLD')):
                    dup.append(oscan_report[i])
                    break
                elif j == int(len(self.new_zap)) - 1:
                    self.unique_openvas.append(oscan_report[i])
                else:
                    continue

    self.new_zap.extend(self.unique_openvas)

    return self.new_zap

 def consolidation2(self, zscan_report, nscan_report, oscan_report,dup1):

    self.unique_nexpose = []
    self.unique_openvas = []
    self.new_zap = zscan_report[:]

    for i in range(len(nscan_report)):
        for j in range(len(self.new_zap)):
            name_nexpose = nscan_report[i][1]
            name_zap = self.new_zap[j][1]

            p = self.common_service.is_duplicate( name_nexpose, name_zap)

            if p >= float(os.getenv('DUPLICATE_MATCH_PERCENTAGE_THRESHOLD')):
                dup1.append(nscan_report[i])
                break
            elif j == int(len(self.new_zap)) - 1:
                self.unique_nexpose.append(nscan_report[i])
            else:
                continue

    self.new_zap.extend(self.unique_nexpose)

    for i in range(len(oscan_report)):
        for j in range(len(self.new_zap)):
            name_openvas = oscan_report[i][1]
            name_zap_nexpose = self.new_zap[j][1]

            cve_openvas = oscan_report[i][4]
            cve_zap_nexpose = self.new_zap[j][4]

            if cve_openvas == cve_zap_nexpose and len(cve_openvas ) >5:
                dup1.append(oscan_report[i])
                break
            else:
                p = self.common_service.is_duplicate( name_openvas, name_zap_nexpose)
                if p >= float(os.getenv('DUPLICATE_MATCH_PERCENTAGE_THRESHOLD')):
                    dup1.append(oscan_report[i])
                    break
                elif j == int(len(self.new_zap)) - 1:
                    self.unique_openvas.append(oscan_report[i])
                else:
                    continue

    self.new_zap.extend(self.unique_openvas)

    return self.new_zap