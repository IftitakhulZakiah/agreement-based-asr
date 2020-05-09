# convert the segment idx into duration
# python convert_segment_to_dur.py <src_file> <dest_file> <dur_of_frame> <frame_shift>
# --- the <src_file> format : segment_idx original_idx start_frame_idx end_frame_idx, e.g. A013C001_001 A013C001 7 15
# --- the start and end frame idx are start from 1, not 0
# --- the script gives <dest_file> format : segment_idx original_idx start_time end_time, e.g. A013C001_001 A013C001 0.07 0.10
# --- the start and end time are in second
# --- <dur_of_frame> is the duration per frame
# --- <frame_shift> is the duration frame shift (e.g. if it 10 ms & dur_of_frame = 25ms, the 15 ms included to the next frame)
# e.g. convert_segment_to_dur.py segments_4_idx.txt segments_4_dur.txt 25 10

from __future__ import division
import sys

in_path = sys.argv[1]
out_path = sys.argv[2]
dur_of_frame = int(sys.argv[3])
frame_shift = int(sys.argv[4])

in_file = open(in_path, 'r')
segments = []
for segment in in_file:
	temp = segment.split()
	# start_time = ((int(temp[2]) - 1) * frame_shift)
	# end_time = (int(temp[3]) * dur_of_frame) - ((int(temp[3]) - 1) * (dur_of_frame - frame_shift))
	start_time = (int(temp[2])) * frame_shift
	end_time = (int(temp[3])) * frame_shift
	segments.append(temp[0] + ' ' + temp[1] + ' ' + str(start_time/1000) + ' ' + str(end_time/1000) + '\n')
in_file.close()

out_file = open(out_path, 'w')
for segment in segments:
	out_file.write(segment)
out_file.close()