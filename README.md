# PYTPMV-NG

PYTPMV-NG is a fork of PYTPMV, this ai slop repo adds flipping support, hopefuly things will get cleaned up later

Python YTPMV-NG generator. Input a MIDI file and video clips, get a rendered YTPMV in video!

## Installation

These scripts require the newest version of Python 3 to work. You only need to do these steps once.
- Download and extract the contents of this repository. If zipped, extract the files and save them in a single folder.
- Install the modules in the `requirements.txt` file using `pip install -r requirements.txt` or your other preferred method.

## Usage

Once installed, you can follow these instructions to run the program each time. Make sure the files `PYTPMVCreator.py` and `PYTPMVHelper.py` stay un-renamed in the same folder.
You will need a MIDI file to convert, and one or more video clips to use as the "instruments" for each track. Open a terminal window in the folder containing the scripts.

### Helper program

This is the recommended method of usage. Upon running `python PYTPMVHelper.py`, follow the wizard presented to you.

### Creator script

Running `python PYTPMVCreator.py` on its own is not advised, as it lacks many of the features, although it can be used to create single-track YTPMVs.
