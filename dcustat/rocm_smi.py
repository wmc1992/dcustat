#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re

sub_space_p = re.compile(r"[ ]{2,}")  # 用于将多个连续空格替换成单个空格


class GetEntryList:
    """

    [root]# rocm-smi

    ==========================System Management Interface ==========================
    ================================================================================
    DCU  Temp   AvgPwr  Fan   Perf    PwrCap  VRAM%  DCU%  
    0    44.0c  20.0W   0.0%  manual  450.0W    0%   0%    
    1    44.0c  19.0W   0.0%  manual  450.0W    0%   0%    
    2    44.0c  18.0W   0.0%  manual  450.0W    0%   0%    
    3    43.0c  20.0W   0.0%  manual  450.0W    0%   0%    
    ================================================================================
    =================================End of SMI Log=================================

    ==========================System Management Interface ==========================
    ================================================================================
    DCU  Temp   AvgPwr   SCLK    MCLK  Fan   Perf    PwrCap  VRAM%  DCU%  
    0    44.0c  20.0W   1250Mhz 800Mhz 0.0%  manual  450.0W    0%   0%    
    1    44.0c  19.0W   1250Mhz 800Mhz 0.0%  manual  450.0W    0%   0%    
    2    44.0c  18.0W   1250Mhz 800Mhz 0.0%  manual  450.0W    0%   0%    
    3    43.0c  20.0W   1250Mhz 800Mhz 0.0%  manual  450.0W    0%   0%    
    ================================================================================
    =================================End of SMI Log=================================

    """

    # DCU id, Temp, AvgPwr, Fan, Perf, PwrCap, VRAM%, DCU%
    pattern = r""
    pattern += r"(\d{1,2})" + r" "  # DCU id
    pattern += r"([\d.]{1,10})c" + r" "  # Temp
    pattern += r"([\d.]{1,10})W" + r" "  # AvgPwr

    pattern += r"(?:\d{1,5}Mhz )?"  # SCLK
    pattern += r"(?:\d{1,5}Mhz )?"  # MCLK

    pattern += r"([\d.]{1,10})%" + r" "  # Fan
    pattern += r"([a-zA-Z]{1,20})" + r" "  # Perf
    pattern += r"([\d.]{1,10})W" + r" "  # PwrCap
    pattern += r"([\d.]{1,10})%" + r" "  # VARN%
    pattern += r"([\d.]{1,10})%"  # DCU%
    pattern = re.compile(pattern)

    def get_entry_list(self, dcu_card_info):
        match_list = []
        for line in dcu_card_info.split("\n"):
            line = sub_space_p.sub(" ", line).strip()
            if self.pattern.search(line):
                match_list.append(self.pattern.search(line).groups())

        entry_list = []
        for card_id, temp, avg_pwr, fan, _, pwr_cap, varn, dcu_percent in match_list:
            entry = dict()
            entry["DCU"] = card_id
            entry["Temp"] = float(temp)
            entry["AvgPwr"] = float(avg_pwr)
            entry["Fan"] = float(fan)
            entry["PwrCap"] = float(pwr_cap)
            entry["VARNPer"] = float(varn)
            entry["DCUPer"] = float(dcu_percent)
            entry_list.append(entry)

        return entry_list


class GetCardStatusWithRocmSmi:

    def new_query(self):
        dcu_card_info = os.popen("rocm-smi").read()
        my_class = GetEntryList()
        entry_list = my_class.get_entry_list(dcu_card_info)
        return entry_list
