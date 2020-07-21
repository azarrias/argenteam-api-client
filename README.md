# aRGENTeaM API client
This little interactive command application allows downloading subtitles (and more) from argenteam.net by using their API.

## Install from source and prerequisites
You can of course just run the .exe included in the [release](https://github.com/azarrias/argenteam-api-client/releases/latest), but if you would rather install from source, the `requirements.txt` file lists all the Python libraries that are needed to run this script.

It is easy and clean to create a virtual environment that satisfies these requirements simply by typing these commands on a system with git, Python3 and virtualenv installed:

```
git clone https://github.com/azarrias/argenteam-api-client.git
cd argenteam-api-client
virtualenv -p python3 env && env\Scripts\activate
python -m pip install -r requirements.txt
```

After installing these required libraries, the script can be run from the command prompt:

```
python argenteam_api_client.py
```

## How to use
It is pretty self explanatory, really. The client will present the user with a series of options, from which it can choose to download subtitles, view details of a movie, tv show or episode, etc.

If you want to search for a particular episode of a tvshow, you must specify it using the sXXeYY naming convention, i.e. "the office s01e01".

Output files will be created within a folder next to the executable. This folder can be deleted and will be created by the executable if missing.
