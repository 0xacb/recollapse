# REcollapse

REcollapse is a helper tool for black-box regex fuzzing to bypass validations and discover normalizations in web applications.

It can also be helpful to bypass WAFs and weak vulnerability mitigations. For more information, take a look at the [REcollapse blog post](https://0xacb.com/2022/11/21/recollapse/).

The goal of this tool is to generate payloads for testing. Actual fuzzing shall be done with other tools like [Burp](https://portswigger.net/burp) (intruder), [ffuf](https://github.com/ffuf/ffuf), or similar.

---------------

### Installation

**Requirements**: Python 3

`pip3 install --user --upgrade -r requirements.txt` or `./install.sh`

**Docker**

`docker build -t recollapse .` or `docker pull 0xacb/recollapse`

---------------

### Usage
```
$ recollapse -h
usage: recollapse [-h] [-p POSITIONS] [-e {1,2,3}] [-r RANGE] [-s SIZE] [-f FILE]
                  [-an] [-mn MAXNORM] [-nt]
                  [input]

REcollapse is a helper tool for black-box regex fuzzing to bypass validations and
discover normalizations in web applications

positional arguments:
  input                 original input

options:
  -h, --help            show this help message and exit
  -p POSITIONS, --positions POSITIONS
                        pivot position modes. Example: 1,2,3,4 (default). 1: starting,
                        2: separator, 3: normalization, 4: termination
  -e {1,2,3}, --encoding {1,2,3}
                        1: URL-encoded format (default), 2: Unicode format, 3: Raw
                        format
  -r RANGE, --range RANGE
                        range of bytes for fuzzing. Example: 0,0xff (default)
  -s SIZE, --size SIZE  number of fuzzing bytes (default: 1)
  -f FILE, --file FILE  read input from file
  -an, --alphanum       include alphanumeric bytes in fuzzing range
  -mn MAXNORM, --maxnorm MAXNORM
                        maximum number of normalizations (default: 3)
  -nt, --normtable      print normalization table
```

---------------

### Detailed options explanation

Let's consider `this_is.an_example` as the input.

**Positions**

1. Fuzz the beginning of the input: `$this_is.an_example`
2. Fuzz the before and after special characters: `this$_$is$.$an$_$example`
3. Fuzz normalization positions: replace all possible bytes according to the [normalization table](https://0xacb.com/normalization_table)
4. Fuzz the end of the input: `this_is.an_example$`

**Encoding**

1. URL-encoded format to be used with `application/x-www-form-urlencoded` or query parameters: `%22this_is.an_example`
2. Unicode format to be used with `application/json`: `\u0022this_is.an_example`
3. Raw format to be used with `multipart/form-data`: `"this_is.an_example`

**Range**

Specify a range of bytes for fuzzing: `-r 1-127`. This will exclude alphanumeric characters unless the `-an` option is provided.

**Size**

Specify the size of fuzzing for positions `1`, `2` and `4`. The default approach is to fuzz all possible values for one byte. Increasing the size will consume more resources and generate many more inputs, but it can lead to finding new bypasses.

**File**

Input can be provided as a positional argument, stdin, or a file through the `-f` option.

**Alphanumeric**

By default, alphanumeric characters will be excluded from output generation, which is usually not interesting in terms of responses. You can allow this with the `-an` option.

**Maximum number or normalizations**

Not all normalization libraries have the same behavior. By default, three possibilities for normalizations are generated for each input index, which is usually enough. Use the `-mn` option to go further.

**Normalization table**

Use the `-nt` option to show the normalization table.

---------------

### Example

```bash
$ recollapse -e 1 -p 1,2,4 -r 10-11 https://legit.example.com
%0ahttps://legit.example.com
%0bhttps://legit.example.com
https%0a://legit.example.com
https%0b://legit.example.com
https:%0a//legit.example.com
https:%0b//legit.example.com
https:/%0a/legit.example.com
https:/%0b/legit.example.com
https://%0alegit.example.com
https://%0blegit.example.com
https://legit%0a.example.com
https://legit%0b.example.com
https://legit.%0aexample.com
https://legit.%0bexample.com
https://legit.example%0a.com
https://legit.example%0b.com
https://legit.example.%0acom
https://legit.example.%0bcom
https://legit.example.com%0a
https://legit.example.com%0b
```

---------------

### Resources

This technique has been presented on [BSidesLisbon 2022](https://bsideslisbon.org/)

**Blog post**: https://0xacb.com/2022/11/21/recollapse/

**Slides**:

- [nahamcon_2022_eu_till_recollapse.pdf](https://github.com/0xacb/recollapse/blob/main/slides/nahamcon_2022_eu_till_recollapse.pdf)
- [bsideslisbon_2022_till_recollapse.pdf](https://github.com/0xacb/recollapse/blob/main/slides/bsideslisbon_2022_till_recollapse.pdf)

**Videos**:

- [NahamCon 2022 EU](https://www.youtube.com/watch?v=1eLTMKWciic)
- [BSidesLisbon 2022](https://www.youtube.com/watch?v=nb91qhj5cOE)

**Normalization table**: https://0xacb.com/normalization_table

---------------

**Thanks**

- [@regala_](https://twitter.com/regala_)
- [@0xz3z4d45](https://twitter.com/0xz3z4d45)
- [@jllis](https://twitter.com/jllis)
- [@samwcyo](https://twitter.com/samwcyo)
- [@yassineaboukir](https://twitter.com/yassineaboukir)
- [@0xteknogeek](https://twitter.com/0xteknogeek)
- [@vgpinho](https://github.com/vgpinho)
- **BBAC**

and

- [@ethiack](https://twitter.com/ethiack) team
- [@0xdisturbance](https://twitter.com/0xdisturbance) team
- [@hacker0x01](https://twitter.com/hacker0x01) team

---------------

### ⚠ Legal Disclaimer ⚠

This project is made for educational and ethical testing purposes only. Usage of this tool for attacking targets without prior mutual consent is illegal. Developers assume no liability and are not responsible for any misuse or damage caused by this tool.
