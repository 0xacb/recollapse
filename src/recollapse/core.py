import contextlib
import itertools
import string
import urllib.parse
import warnings
from typing import ClassVar, Optional

import unidecode
from prettytable import PrettyTable

warnings.simplefilter("ignore")


HTML_HEADER = """<!DOCTYPE html>
<meta charset="utf-8">
<html>
<head>
<style>
body {
    background: black;
    color: green;
}
table {
    font-size: 13px !important;
}
</style>
</head>
<body>"""

HTML_FOOTER = "</body></html>"


class Recollapse:
    ENCODING_URL = 1
    ENCODING_UNICODE = 2
    ENCODING_RAW = 3
    ENCODING_DOUBLE_URL = 4

    MODE_START = 1
    MODE_SEP = 2
    MODE_NORM = 3
    MODE_TERM = 4
    MODE_RE_META = 5
    MODE_CASE = 6
    MODE_TRUNC = 7
    MODES_ALL = [MODE_START, MODE_SEP, MODE_NORM,
                MODE_TERM, MODE_RE_META, MODE_CASE,
                MODE_TRUNC]

    REGEX_METACHARS = ".^$*+-?()[]{}\\|"

    DEFAULT_SIZE = 1
    DEFAULT_ENCODING = ENCODING_RAW
    DEFAULT_ENCODING_CLI = ENCODING_URL
    DEFAULT_RANGE = [0, 255]
    DEFAULT_MODES = MODES_ALL
    DEFAULT_MAX_NORM = 3
    DEFAULT_MAX_TRUNC = 3

    normalization_d: ClassVar[dict] = {}
    truncation_d: ClassVar[dict] = {}
    case_d: ClassVar[dict] = {}


    def __init__(self, size: int = DEFAULT_SIZE,
                 encoding: int = DEFAULT_ENCODING,
                 range: list = DEFAULT_RANGE,
                 modes: list = DEFAULT_MODES,
                 input: Optional[str] = None,
                 file: Optional[str] = None,
                 normtable: bool = False,
                 trunctable: bool = False,
                 casetable: bool = False,
                 html: bool = False,
                 alphanum: bool = False,
                 maxnorm: int = DEFAULT_MAX_NORM,
                 maxtrunc: int = DEFAULT_MAX_TRUNC) -> None:
        for param, value in locals().items():
            if param != "self":
                setattr(self, param, value)


    def run(self) -> None:
        if self.normtable:
            if not self.normalization_d:
                self._build_normalization_dict()
            self.print_normalization_table()
            return
        
        if self.trunctable:
            if not self.truncation_d:
                self._build_truncation_dict()
            self.print_truncation_table()
            return
        
        if self.casetable:
            if not self.case_d:
                self._build_case_dict()
            self.print_case_table()
            return
        
        if not self.input:
            if self.file:
                with open(self.file) as f:
                    self.input = f.readlines()[0].rstrip()
        
        if not self.input:
            return
            
        inputs = self.input.split("\n")
        outputs = []
        for input in inputs:
            outputs.extend(self.generate(input))

        print("\n".join(sorted(set(outputs))))


    def generate(self, input: str) -> list[str]:
        variants = []

        fuzzing_range = range(self.range[0], self.range[1]+1)
        if not self.alphanum:
            alphanum_ascii = list(map(ord, string.ascii_letters + string.digits))
            fuzzing_range = [b for b in list(fuzzing_range) if b not in alphanum_ascii]

        if self.MODE_START in self.modes:
            for t in itertools.product(fuzzing_range, repeat=self.size):
                variants.extend(self._generate_variants_for_index(input, t, 0))

        if self.MODE_SEP in self.modes:
            for i in range(len(input)):
                c = input[i]
                if c in string.punctuation:
                    for t in itertools.product(fuzzing_range, repeat=self.size):
                        variants.extend(self._generate_variants_for_index(input, t, i))
                        variants.extend(self._generate_variants_for_index(input,t, i+1))

        if self.MODE_NORM in self.modes:
            if not self.normalization_d:
                self._build_normalization_dict()
            
            for i in range(len(input)):
                c = input[i]
                if c in self.normalization_d:
                    for cc in self.normalization_d.get(c)[:self.maxnorm]:
                        variants.extend(self._generate_variants_for_index(input, (ord(cc),), i, replace=True))

        if self.MODE_TERM in self.modes:
            for t in itertools.product(fuzzing_range, repeat=self.size):
                variants.extend(self._generate_variants_for_index(input,t, len(input)))

        if self.MODE_RE_META in self.modes:
            for i in range(len(input)):
                c = input[i]
                if c in self.REGEX_METACHARS:
                    for t in itertools.product(fuzzing_range, repeat=self.size):
                        variants.extend(self._generate_variants_for_index(input, t, i, replace=True))

        if self.MODE_CASE in self.modes:
            if not self.case_d:
                self._build_case_dict()
            
            for i in range(len(input)):
                c = input[i]
                if c in self.case_d:
                    for cc in self.case_d.get(c):
                        variants.extend(self._generate_variants_for_index(input, (ord(cc),), i, replace=True))

        if self.MODE_TRUNC in self.modes:
            if not self.truncation_d:
                self._build_truncation_dict()
            
            for i in range(len(input)):
                c = input[i]
                if c in self.truncation_d:
                    for cc in self.truncation_d.get(c)[:self.maxtrunc]:
                        variants.extend(self._generate_variants_for_index(input, (ord(cc),), i, replace=True))
        
        return sorted(set(variants))


    def _generate_variants_for_index(self, s: str,
                                     bytes: tuple[int],
                                     index: int,
                                     replace: bool = False) -> list[str]:
        a = s[:index]
        b = s[index:]
        
        index_variants = []

        if replace:
            a = s[:index]
            b = s[index+1:]

        x = ""
        if self.encoding == self.ENCODING_URL:
            for byte in bytes:
                if byte > 0xff:
                    x += urllib.parse.quote(chr(byte)).lower()
                else:
                    x += f"%{hex(byte)[2:].zfill(2)}"
            index_variants.append(f"{a}{x}{b}")
        elif self.encoding == self.ENCODING_RAW:
            for byte in bytes:
                if 10 <= byte < 13 or byte == 27:
                    continue
                x += chr(byte)
            with contextlib.suppress(UnicodeEncodeError):
                index_variants.append(f"{a}{x}{b}")
        elif self.encoding == self.ENCODING_UNICODE:
            for byte in bytes:
                x += f"\\u{hex(byte)[2:].zfill(4)}"
            index_variants.append(f"{a}{x}{b}")
        elif self.encoding == self.ENCODING_DOUBLE_URL:
            for byte in bytes:
                if byte > 0xff:
                    x += urllib.parse.quote(chr(byte))
                else:
                    x += f"%{hex(byte)[2:].zfill(2)}"
            index_variants.append(f"{a}{urllib.parse.quote(x).lower()}{b}")

        return index_variants

    
    def _build_truncation_dict(self) -> None:
        for i in range(0x0, 0x100):
            self.truncation_d[chr(i)] = []
        
        for c in range(0x110000):
            if 0xd800 <= c <= 0xdfff:
                continue
            low_byte = c & 0xff
            char_c = chr(c)
            try:
                ascii_c = chr(low_byte)
                if ascii_c != char_c and not self.truncation_d.get(char_c):
                    self.truncation_d[ascii_c].append(char_c)
            except UnicodeEncodeError:
                continue
    

    def _build_normalization_dict(self) -> None:
        charset = [chr(c) for c in range(0x20,0x7f)]
        for c in charset:
            self.normalization_d[c] = []

        for c in range(0x110000):
            if 0xd800 <= c <= 0xdfff:
                continue
            char = chr(c)
            norm_c = unidecode.unidecode(char)
            if len(norm_c) == 1 and norm_c in charset and norm_c != char:
                self.normalization_d[norm_c].append(char)


    def _build_case_dict(self) -> None:
        for c in range(0x110000):
            if 0xd800 <= c <= 0xdfff:
                continue
            char = chr(c)
            for case_c in [char.upper(), char.lower(), char.casefold()]:
                if (
                    len(case_c) == 1
                ):
                    if case_c != char:
                        if not self.case_d.get(case_c):
                            self.case_d[case_c] = []
                        if char not in self.case_d[case_c]:
                            self.case_d[case_c].append(char)

        self.case_d = dict(sorted(self.case_d.items(), key=lambda item: item[0]))


    def print_table(self, table_d: dict, html: bool = False) -> None:
        table = []
        headers = []

        max_col = len(table_d[max(table_d, key=lambda k: len(table_d[k]))])

        for c in table_d:
            l = table_d.get(c)
            l = l + [""] * (max_col - len(l))
            if html:
                headers.append(hex(ord(c)))
                table.append([c, *l])
            else:
                table.append([hex(ord(c)), c, *l])

        tab = PrettyTable()
        tab.header = html
        tab.border = False

        if html:
            transpose_table = list(zip(*table))
            tab.field_names = headers
            tab.add_rows(transpose_table)
            print(HTML_HEADER)
            print(tab.get_html_string())
            print(HTML_FOOTER)
        else:
            tab.add_rows(table)
            print(tab)

    def print_normalization_table(self) -> None:
        self.print_table(self.normalization_d, self.html)
    

    def print_truncation_table(self) -> None:
        self.print_table(self.truncation_d, self.html)
    

    def print_case_table(self) -> None:
        self.print_table(self.case_d, self.html)
