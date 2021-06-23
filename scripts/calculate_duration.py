# How to run
# python calculate_duration.py mfcc/sample_200128/unlabeled/wav.scp

import wave
import contextlib
import os
import datetime
import sys

path=sys.argv[1]

path_files = []
wav_scp = open(path)
for utt in wav_scp:
	temp_path = utt.split()[1]
	path_files.append(temp_path)


total_duration = 0
for fname in path_files:
	print(fname)
	with contextlib.closing(wave.open(fname,'r')) as f:
	    frames = f.getnframes()
	    rate = f.getframerate()
	    duration = frames / float(rate)
	    total_duration += duration

print('Duration ' + str(datetime.timedelta(seconds=total_duration)) + ' with ' + str(len(path_files)) + ' files')