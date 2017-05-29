# wsSp1d3R

wsSp1d3R are scripts to visualize academic information of people in ESPOL
These scripts work with [Python 3](https://www.python.org/) :snake: :stuck_out_tongue_winking_eye:

## Setup:


### Set credentials in the environment variables :new_moon_with_face:

```bash
export SPIDER_USER="your user"
export SPIDER_KEY="your key"
```

**Don't forget to reload your shell** :unamused:

### Install dependencies:

`pip3 install -r requirements.txt`

## Run Scripts:

### wsSpider
-----

&nbsp; wsSpider returns a student's grades in one year and specific academic term.

&nbsp; `python3 wsSpider.py <name> <lastname> <year> <term>`

&nbsp; **Examples:**

&nbsp; `python3 wsSpider.py John Doe 2017 1`

&nbsp; `python3 wsSpider.py Oscar 'De la Olla' 2014 2`