#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import locale
import os
import platform
import sys
from datetime import datetime

from blessed import Terminal
from six.moves import cStringIO as StringIO

from .rocm_smi import GetCardStatusWithRocmSmi


IS_WINDOWS = "windows" in platform.platform().lower()


class DCU:
    """ 该类表示每个 DCU 的信息 """

    def __init__(self, entry, term, light=False, *args, **kwargs):
        if not isinstance(entry, dict):
            raise TypeError("entry should be a dict, {} given".format(type(entry)))
        self.entry = entry
        self.term = term
        self.light = light

    def __repr__(self):
        return self.print_to(StringIO()).getvalue()

    def keys(self):
        return self.entry.keys()

    def __getitem__(self, key):
        return self.entry[key]

    @property
    def card_id(self):
        return self.entry["DCU"]

    @property
    def temp(self):
        return self.entry["Temp"]

    @property
    def avg_pwr(self):
        return self.entry["AvgPwr"]

    @property
    def fan(self):
        return self.entry["Fan"]

    @property
    def pwr_cap(self):
        return self.entry["PwrCap"]

    @property
    def varn(self):
        return self.entry["VARNPer"]

    @property
    def dcu_percent(self):
        return self.entry["DCUPer"]

    def get_color(self):
        def _conditional(cond_fn, true_value, false_value, error_value=self.term.bold_black):
            try:
                return cond_fn() and true_value or false_value
            except Exception:
                return error_value

        colors = dict()
        colors["C0"] = self.term.normal
        colors["C1"] = self.term.cyan

        if self.light:
            colors["DCUtemp"] = self.term.bold_red
        else:
            colors["DCUtemp"] = _conditional(lambda: self.temp < 60, self.term.red, self.term.bold_red)

        if self.light:
            colors["DCUfan"] = self.term.bold_blue
        else:
            colors["DCUfan"] = _conditional(lambda: self.fan < 50, self.term.blue, self.term.bold_blue)

        colors["DCUavg_pwr"] = self.term.bold_yellow

        if self.light:
            colors["DCUpwr_cap"] = self.term.bold_yellow
        else:
            colors["DCUpwr_cap"] = self.term.yellow

        if self.light:
            colors["DCUvarn"] = self.term.bold_green
        else:
            colors["DCUvarn"] = _conditional(lambda: self.varn < 50, self.term.green, self.term.bold_green)

        if self.light:
            colors["DCUdcu_percent"] = self.term.bold_green
        else:
            colors["DCUdcu_percent"] = _conditional(lambda: self.dcu_percent < 50, self.term.green, self.term.bold_green)

        return colors

    def print_to(self, fp, *args, **kwargs):
        colors = self.get_color()

        # build one-line display information
        reps = ""
        reps += "%(C1)s[{entry[DCU]}]%(C0)s" + " "
        reps += "%(DCUtemp)s{entry[Temp]:>4}°C%(C0)s" + ", "
        reps += "%(DCUfan)s{entry[Fan]:>4} %%%(C0)s, "
        reps += "%(C1)s%(DCUavg_pwr)s{entry[AvgPwr]:>5}W%(C0)s" + " / " + "%(DCUpwr_cap)s{entry[PwrCap]:>5}W%(C0)s, "
        reps += "%(DCUvarn)s{entry[VARNPer]:>4} %%%(C0)s, "
        reps += "%(DCUdcu_percent)s{entry[DCUPer]:>4} %%%(C0)s"

        def _repr(v, none_value="??"):
            return none_value if v is None else v

        reps = reps % colors
        reps = reps.format(entry={k: _repr(v) for k, v in self.entry.items()})
        fp.write(reps)
        return fp


class DCUCardCollection:
    """ 当前机器上所有 DCU 的信息 """

    def __init__(self, entry_list, eol_char=os.linesep, force_color=False, light=False, *args, **kwargs):
        self.hostname = platform.node()
        self.query_time = datetime.now()
        self.eol_char = eol_char
        self.term = self.get_term(force_color)

        # 是否以较亮的模式显示，如果指定了该参数，那么所有的字段都使用加粗显示
        self.light = light  

        self.title_colors = self.get_title_colors()

        dcu_list = []
        for entry in entry_list:
            dcu_list.append(DCU(entry, self.term, light=light, *args, **kwargs))
        self.dcu_list = dcu_list

    def get_term(self, force_color=False):
        if force_color:
            TERM = os.getenv("TERM") or "xterm-256color"
            t_color = Terminal(kind=TERM, force_styling=True)

            # workaround of issue #32 (watch doesn"t recognize sgr0 characters)
            t_color._normal = u"\x1b[0;10m"
        else:
            t_color = Terminal()  # auto, depending on isatty
        return t_color

    def print_header(self, fp, eol_char, term):
        if IS_WINDOWS:
            # no localization is available; just use a reasonable default same as str(time_str) but without ms
            time_str = self.query_time.strftime("%Y-%m-%d %H:%M:%S")
        else:
            time_format = locale.nl_langinfo(locale.D_T_FMT)
            time_str = self.query_time.strftime(time_format)

        header_template = "{t.bold_white}{hostname}{t.normal}  "
        header_template += "{time_str}"

        header_msg = header_template.format(
            hostname=self.hostname,
            time_str=time_str,
            t=term,
        )

        fp.write(header_msg.strip())
        fp.write(eol_char)

    def get_title_colors(self):
        colors = dict()
        colors["C0"] = self.term.normal
        colors["C1"] = self.term.cyan
        colors["temp"] = self.term.bold_red if self.light else self.term.red
        colors["fan"] = self.term.bold_blue if self.light else self.term.blue
        colors["avg_pwr"] = self.term.bold_yellow
        colors["pwr_cap"] = self.term.bold_yellow if self.light else self.term.yellow
        colors["varn"] = self.term.bold_green if self.light else self.term.green
        colors["dcu_percent"] = self.term.bold_green if self.light else self.term.green
        return colors

    def print_title(self, fp, eol_char):
        title = "%(C1)s{entry[ID]:>3}%(C0)s" + " "
        title += "%(temp)s{entry[Temp]:>4}%(C0)s" + ", "
        title += "%(fan)s{entry[Fan]:>4}%(C0)s" + ", "
        title += "%(avg_pwr)s{entry[AvgPwr]:>6}%(C0)s" + " / "
        title += "%(pwr_cap)s{entry[PwrCap]:>6}%(C0)s" + ", "
        title += "%(varn)s{entry[VARM]:>4}%(C0)s" + ", "
        title += "%(dcu_percent)s{entry[DCU]:>5}%(C0)s"

        def _repr(v, none_value="??"):
            return none_value if v is None else v

        title = title % self.title_colors
        my_dict = {"ID": "ID", "Temp": "温度", "Fan": "风扇", "AvgPwr": "AvgPwr", 
                   "PwrCap": "PwrCap", "VARM": "显存", "DCU": "Core"}
        title = title.format(entry={k: _repr(v) for k, v in my_dict.items()})

        fp.write(title.strip())
        fp.write(eol_char)

    def print_formatted(self, fp=sys.stdout, *args, **kwargs):
        # header
        self.print_header(fp=fp, eol_char=self.eol_char, term=self.term)

        # title
        self.print_title(fp=fp, eol_char=self.eol_char)

        # body
        for dcu in self:
            dcu.print_to(fp)
            fp.write(self.eol_char)

        fp.flush()
        return fp

    def jsonify(self):
        return {
            "hostname": self.hostname,
            "query_time": self.query_time,
            "dcu": [dcu.jsonify() for dcu in self]
        }

    def print_json(self, fp=sys.stdout):
        def date_handler(obj):
            if hasattr(obj, "isoformat"):
                return obj.isoformat()
            else:
                raise TypeError(type(obj))

        o = self.jsonify()
        json.dump(o, fp, indent=4, separators=(",", ": "), default=date_handler)
        fp.write(os.linesep)
        fp.flush()

    def __len__(self):
        return len(self.dcu_list)

    def __iter__(self):
        return iter(self.dcu_list)

    def __getitem__(self, index):
        return self.dcu_list[index]

    def __repr__(self):
        s = "DCUCollection(host=%s, [\n" % self.hostname
        s += "\n".join("  " + str(g) for g in self.dcu_list)
        s += "\n])"
        return s


def new_query(*args, **kwargs):
    """Query the information of all the DCU on local machine"""

    entry_list = GetCardStatusWithRocmSmi().new_query()

    return DCUCardCollection(entry_list, *args, **kwargs)
