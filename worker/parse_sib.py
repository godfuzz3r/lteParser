#!/usr/bin/env python3
import tailer
import sys
import time
import json
from pprint import pprint

def read_line(log):
    buffer_line = ''
    while 1:
        line = log.readline()
        if not len(line):
            continue

        buffer_line += line
        if buffer_line[-1] == '\n':
            return buffer_line

def parse_content(log):
    content = ''
    while 1:
        if log.readline() == '[\n':
            break

    while 1:
        line = log.readline()
        if line == ']\n':
            break
        if len(line):
            content += line

    return content

file_name = '/tmp/ue.log'
if '-f' in sys.argv:
    file_name = sys.argv[sys.argv.index('-f')+1]

verbose = False
if "-v" in sys.argv:
    verbose = True

timeout = 30
if "-t" in sys.argv:
    timeout = sys.argv[sys.argv.index('-t')+1]

file_error = True

while file_error:
    try:
        log = open(file_name)
        file_error = False
    except FileNotFoundError:
        file_error = True

mib = sib1 = sib2 = sib3 = sib4 = sib5 = sib6 = sib7 = sib8 = sib9 = sib10 = sib11 = sib12 = sib13 = False
sib3Present = sib4Present = sib5Present = sib6Present = sib7Present = sib8Present = sib9Present = sib10Present = sib11Present = sib12Present = sib13Present = False
content = ''
parsed_data = {}

timeout = time.time() + 30
required_sibs = 1

while 1:
    if time.time() > timeout:
        print(json.dumps(parsed_data))
        exit()
    if sib1 and not required_sibs or sib5:
        print(json.dumps(parsed_data))
        exit()
    line = read_line(log)
    if 'Rx MIB' in line:
        content = parse_content(log)
        if not mib:
            # Reading MIB
            mib = True
            MIB = json.loads(content)["BCCH-BCH-Message"]
            parsed_data["mib"] = MIB
            timeout += 30
            if verbose:
                sys.stderr.write("Found MIB, increasing timeout to 30 sec\n")
                sys.stderr.write(json.dumps({"mib": MIB}, indent=4))

    if '[D] Content' in line:
        content = parse_content(log)
        if 'systemInformationBlockType1' in content and not sib1:
            sib1 = True
            SIB1 = json.loads(content)["BCCH-DL-SCH-Message"]["message"]["c1"]["systemInformationBlockType1"]
            parsed_data["sib1"] = SIB1
            timeout += 30
            if verbose:
                sys.stderr.write(json.dumps({"sib1": SIB1}, indent=4))
            required_sibs = len(SIB1["schedulingInfoList"])

        if 'sib2' in content and not sib2:
            sib2 = True
            if not 'sib2' in parsed_data:
                SIB2 = json.loads(content)["BCCH-DL-SCH-Message"]["message"]["c1"]["systemInformation"]["criticalExtensions"]["systemInformation-r8"]["sib-TypeAndInfo"]
                parsed_data['sib2'] = SIB2
                timeout += 30
                if verbose:
                    sys.stderr.write(json.dumps({"sib2": SIB2}, indent=4))
                required_sibs -= 1

        if 'sib3' in content and not sib3:
            sib3 = True
            if not 'sib3' in parsed_data:
                SIB3 = json.loads(content)["BCCH-DL-SCH-Message"]["message"]["c1"]["systemInformation"]["criticalExtensions"]["systemInformation-r8"]["sib-TypeAndInfo"]
                parsed_data['sib3'] = SIB3
                if verbose:
                    sys.stderr.write(json.dumps({"sib3": SIB3}, indent=4))
                required_sibs -= 1

        if 'sib4' in content and not sib4:
            sib4 = True
            if not 'sib4' in parsed_data:
                SIB4 = json.loads(content)["BCCH-DL-SCH-Message"]["message"]["c1"]["systemInformation"]["criticalExtensions"]["systemInformation-r8"]["sib-TypeAndInfo"]
                parsed_data['sib4'] = SIB4
                if verbose:
                    sys.stderr.write(json.dumps({"sib4": SIB4}, indent=4))
                required_sibs -= 1

        if 'sib5' in content and not sib5:
            sib5 = True
            if not 'sib5' in parsed_data:
                SIB5 = json.loads(content)["BCCH-DL-SCH-Message"]["message"]["c1"]["systemInformation"]["criticalExtensions"]["systemInformation-r8"]["sib-TypeAndInfo"][0]["sib5"]
                parsed_data['sib5'] = SIB5
                if verbose:
                    sys.stderr.write(json.dumps({"sib5": SIB5}, indent=4))
                required_sibs = -1

        if 'sib6' in content and not sib6:
            sib6 = True
            if not 'sib6' in parsed_data:
                SIB6 = json.loads(content)["BCCH-DL-SCH-Message"]["message"]["c1"]["systemInformation"]["criticalExtensions"]["systemInformation-r8"]["sib-TypeAndInfo"]
                parsed_data['sib6'] = SIB6
                if verbose:
                    sys.stderr.write(json.dumps({"sib6": SIB6}, indent=4))
                required_sibs -= 1

        if 'sib7' in content and not sib7:
            sib7 = True
            if not 'sib7' in parsed_data:
                SIB7 = json.loads(content)["BCCH-DL-SCH-Message"]["message"]["c1"]["systemInformation"]["criticalExtensions"]["systemInformation-r8"]["sib-TypeAndInfo"]
                parsed_data['sib7'] = SIB7
                if verbose:
                    sys.stderr.write(json.dumps({"sib7": SIB7}, indent=4))
                required_sibs -= 1

        if 'sib8' in content and not sib8:
            sib8 = True
            if not 'sib8' in parsed_data:
                SIB8 = json.loads(content)["BCCH-DL-SCH-Message"]["message"]["c1"]["systemInformation"]["criticalExtensions"]["systemInformation-r8"]["sib-TypeAndInfo"]
                parsed_data['sib8'] = SIB8
                if verbose:
                    sys.stderr.write(json.dumps({"sib8": SIB8}, indent=4))
                required_sibs -= 1

        if 'sib9' in content and not sib9:
            sib9 = True
            if not 'sib9' in parsed_data:
                SIB9 = json.loads(content)["BCCH-DL-SCH-Message"]["message"]["c1"]["systemInformation"]["criticalExtensions"]["systemInformation-r8"]["sib-TypeAndInfo"]
                parsed_data['sib9'] = SIB9
                if verbose:
                    sys.stderr.write(json.dumps({"sib9": SIB9}, indent=4))
                required_sibs -= 1

        if 'sib10' in content and not sib10:
            sib10 = True
            if not 'sib10' in parsed_data:
                SIB10 = json.loads(content)["BCCH-DL-SCH-Message"]["message"]["c1"]["systemInformation"]["criticalExtensions"]["systemInformation-r8"]["sib-TypeAndInfo"]
                parsed_data['sib10'] = SIB10
                if verbose:
                    sys.stderr.write(json.dumps({"sib10": SIB10}, indent=4))
                required_sibs -= 1

        if 'sib11' in content and not sib11:
            sib11 = True
            if not 'sib11' in parsed_data:
                SIB11 = json.loads(content)["BCCH-DL-SCH-Message"]["message"]["c1"]["systemInformation"]["criticalExtensions"]["systemInformation-r8"]["sib-TypeAndInfo"]
                parsed_data['sib11'] = SIB11
                if verbose:
                    sys.stderr.write(json.dumps({"sib11": SIB11}, indent=4))
                required_sibs -= 1

        if 'sib12' in content and not sib12:
            sib12 = True
            if not 'sib12' in parsed_data:
                SIB2 = json.loads(content)["BCCH-DL-SCH-Message"]["message"]["c1"]["systemInformation"]["criticalExtensions"]["systemInformation-r8"]["sib-TypeAndInfo"]
                parsed_data['sib12'] = SIB12
                if verbose:
                    sys.stderr.write(json.dumps({"sib12": SIB12}, indent=4))
                required_sibs -= 1

        if 'sib13' in content and not sib13:
            sib13 = True
            if not 'sib13' in parsed_data:
                SIB2 = json.loads(content)["BCCH-DL-SCH-Message"]["message"]["c1"]["systemInformation"]["criticalExtensions"]["systemInformation-r8"]["sib-TypeAndInfo"]
                parsed_data['sib13'] = SIB13
                if verbose:
                    sys.stderr.write(json.dumps({"sib13": SIB13}, indent=4))
                required_sibs -= 1
