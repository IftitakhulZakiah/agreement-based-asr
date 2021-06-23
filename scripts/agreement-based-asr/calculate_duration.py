# How to run
# python calculate_duration.py ..\\test-QA\\wavs
# ..\\test-QA\\wavs is the directory which contain wav files per speaker

import wave
import contextlib
import os
import datetime
import sys

path=sys.argv[1]

path_files=[]
for root, dirs, files in os.walk(path):
	for file in files:
		path_files.append(root+'//'+file)


total_duration = 0
for fname in path_files:
	print(fname)
	with contextlib.closing(wave.open(fname,'r')) as f:
	    frames = f.getnframes()
	    rate = f.getframerate()
	    duration = frames / float(rate)
	    total_duration += duration

print('Duration ' + str(datetime.timedelta(seconds=total_duration)) + ' with ' + str(len(path_files)) + ' files')