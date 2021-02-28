# iev-data-extraction-tools
Tools for converting IEV data in Glossarist Desktop format to new registry format used by Paneron extension

**How to install**

Setup virtual ENV:
`python3 -m venv ./venv`

Activate it:
`source ./venv/bin/activate`

Then install requirements:
`pip3 install -r requirements.txt`

Copy `config.py.sample` to `config.py`, then edit it:

`input_dir` - path to dir with data in old Glossarist Desktop format

`output_dir` - path to dir for new format (results)

`default_date` - date used by default for items without date

`default_status` - item status used by default for items without status

`source_limit` - convert less or equal files in old Glossarist Desktop format (`None` means convert all files)

**Usage**

Run `python3 convert.py` (don't forget about venv).
