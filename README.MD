Runtastic Converter
==================

Utility for converting the JSON files of an exported Runtastic profile to .tcx files.

### Usage

- Export your Runtastic profile as described here:  
https://help.runtastic.com/hc/en-us/articles/360000953365-Export-Account-Data

- Leave the folder structure of the extracted profile data intact.  
**To clarify:** In the folder, where your session data
resides as .json files has to be the subdirectory "GPS-data" in where the gps data files resides as .json files.

- Execute the program:  
```$ python convert_sessions.py $INDIR $OUTDIR```  
where ```$INDIR``` is the path to your session data folder (The Sport-sessions folder in your export) and ```$OUTDIR```
is the folder where you want to save your .tcx files. 