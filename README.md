# REcollapse

REcollapse is a helper tool for black-box regex fuzzing to bypass validations and discover normalizations in web applications.

It can also be helpful to bypass WAFs and weak vulnerability mitigations. For more information, take a look at the [REcollapse blog post](https://0xacb.com/2022/11/21/recollapse/).

The goal of this tool is to generate payloads for testing. Actual fuzzing shall be done with other tools like [Burp](https://portswigger.net/burp) (intruder), [Caido](https://caido.io) (automate), [ffuf](https://github.com/ffuf/ffuf), or similar.

---------------

### Installation

**Requirements**: Python 3

`python3 setup.py install` or `pip3 install .`

**Docker**

`docker build -t recollapse .` or `docker pull 0xacb/recollapse`

---------------

### Usage
```
$ recollapse -h
usage: recollapse [-h] [-m MODES] [-e {1,2,3,4}] [-r RANGE] [-s SIZE] [-f FILE] [-an] [-mn MAXNORM] [-mt MAXTRUNC] [-nt] [-tt] [-ct]
                  [--html] [--version]
                  [input]

REcollapse is a helper tool for black-box regex fuzzing to bypass validations and discover normalizations in web applications

positional arguments:
  input                 original input

options:
  -h, --help            show this help message and exit
  -m, --modes, -p, --positions MODES
                        variation modes. Example: 1,2,3,4,5,6,7 (default). 1: starting, 2: separator, 3: normalization, 4:
                        termination, 5: regex metacharacters, 6: case folding/upper/lower, 7: byte truncation
  -e, --encoding {1,2,3,4}
                        1: URL-encoded format (default), 2: Unicode format, 3: Raw format, 4: Double URL-encoded format
  -r, --range RANGE     range of bytes for fuzzing. Example: 0,0xff (default)
  -s, --size SIZE       number of fuzzing bytes (default: 1)
  -f, --file FILE       read input from file
  -an, --alphanum       include alphanumeric bytes in fuzzing range
  -mn, --maxnorm MAXNORM
                        maximum number of normalizations (default: 3)
  -mt, --maxtrunc MAXTRUNC
                        maximum number of truncations (default: 3)
  -nt, --normtable      print normalization table
  -tt, --trunctable     print truncation table
  -ct, --casetable      print case table
  --html                output tables in HTML format
  --version             show recollapse version
```

---------------

### Detailed options explanation

Let's consider `this_is.an_example` as the input.

**Modes**

1. Fuzz the beginning of the input: `$this_is.an_example`
2. Fuzz the before and after special characters: `this$_$is$.$an$_$example`
3. Fuzz normalization positions: replace all possible bytes according to the [normalization table](https://0xacb.com/normalization_table)
4. Fuzz the end of the input: `this_is.an_example$`
5. Fuzz regex metacharacters: replace all possible regex metacharacters: `.^$*+-?()[]{}\|`
6. Fuzz case folding/upper/lower: replace all possible bytes according to the [case table](https://0xacb.com/case_table)
7. Fuzz byte truncation: replace all possible bytes according to the [truncation table](https://0xacb.com/truncation_table)

**Encoding**

1. URL-encoded format to be used with `application/x-www-form-urlencoded` or query/body parameters: `%22this_is.an_example`
2. Unicode format to be used with `application/json`: `\u0022this_is.an_example`
3. Raw format to be used with `multipart/form-data`: `"this_is.an_example`
4. Double URL-encoded format

**Range**

Specify a range of bytes for fuzzing: `-r 1-127`. This will exclude alphanumeric characters unless the `-an` option is provided.

**Size**

Specify the size of fuzzing for modes `1`, `2` and `4`. The default approach is to fuzz all possible values for one byte. Increasing the size will consume more resources and generate many more inputs, but it can lead to finding new bypasses.

**File**

Input can be provided as a positional argument, stdin, or a file through the `-f` option.

**Alphanumeric**

By default, alphanumeric characters will be excluded from output generation, which is usually not interesting in terms of responses. You can allow this with the `-an` option.

**Maximum number or normalizations**

Not all normalization libraries have the same behavior. By default, three possibilities for normalizations are generated for each input index, which is usually enough. Use the `-mn` option to go further.

**Tables**

Use the `-nt` option to show the normalization table, the `-ct` option to show the case table, and the `-tt` option to show the truncation table. You can also use the `--html` option to output tables in HTML format.

```bash
$ recollapse -nt --html > normalization_table.html
$ recollapse -tt --html > truncation_table.html
$ recollapse -ct --html > case_table.html
```

---------------

### Examples

Using Recollapse as a command-line tool:

```bash
$ recollapse -e 1 -m 1,2,4 -r 10-11 https://legit.example.com
%0ahttps://legit.example.com
%0bhttps://legit.example.com
https%0a://legit.example.com
https%0b://legit.example.com
...

$ echo "a@b.com" | recollapse 
%00a@b.com
%01a@b.com
...

$ echo "<svg/onload=alert(1)>" | recollapse | ffuf -w - -u "https://example.com/?param=FUZZ" -mc 200,403,500
```

Using Recollapse as a library:

```python
from recollapse import Recollapse

recollapse = Recollapse(modes=Recollapse.DEFAULT_MODES,
                        encoding=Recollapse.ENCODING_RAW)
variants = recollapse.generate("<script")
for variant in variants:
    print(variant)
```

---------------

### Resources

This technique was originally presented on [BSidesLisbon 2022](https://bsideslisbon.org/)

**Blog post**: https://0xacb.com/2022/11/21/recollapse/

**Slides**:

- [nahamcon_2022_eu_till_recollapse.pdf](https://github.com/0xacb/recollapse/blob/main/slides/nahamcon_2022_eu_till_recollapse.pdf)
- [bsideslisbon_2022_till_recollapse.pdf](https://github.com/0xacb/recollapse/blob/main/slides/bsideslisbon_2022_till_recollapse.pdf)

**Videos**:

- [NahamCon 2022 EU](https://www.youtube.com/watch?v=1eLTMKWciic)
- [BSidesLisbon 2022](https://www.youtube.com/watch?v=nb91qhj5cOE)

**Tables**:

- **Normalization table**: https://0xacb.com/normalization_table
- **Case table**: https://0xacb.com/case_table
- **Truncation table**: https://0xacb.com/truncation_table

---------------

**Thanks**

- [@regala_](https://x.com/regala_)
- [@0xz3z4d45](https://x.com/0xz3z4d45)
- [@jllis](https://x.com/jllis)
- [@samwcyo](https://x.com/samwcyo)
- [@yassineaboukir](https://x.com/yassineaboukir)
- [@0xteknogeek](https://x.com/0xteknogeek)
- [@vgpinho](https://github.com/vgpinho)
- [@ryancbarnett](https://x.com/ryancbarnett)
- **BBAC**

and

- [@ethiack](https://x.com/ethiack) team
- [@0xdisturbance](https://x.com/0xdisturbance) team
- [@hacker0x01](https://x.com/hacker0x01) team

---------------

### ⚠ Legal Disclaimer ⚠

This project is made for educational and ethical testing purposes only. Usage of this tool for attacking targets without prior mutual consent is illegal. Developers assume no liability and are not responsible for any misuse or damage caused by this tool.
