# split the 'majority' (4) segment and not 'majority'
# python split_4_and_not.py <src_file> <dest_dir>
# e.g. python split_4_and_not.py count_vote.txt segments/

import sys
import argparse

def get_args():
    """Get the input arguments from the stdin."""

    parser = argparse.ArgumentParser(description="Split the majority segments.",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("--suffix", type=str, help="suffix for the out file")
    parser.add_argument("src_file", type=str, metavar="source file")
    parser.add_argument("dest_dir", type=str, metavar="desttionation directory")
    
    return parser.parse_args()


def convert_to_3_digit(idx):
	idx_3_digit = ''
	if idx < 10:
		idx_3_digit = '00' + str(idx)
	elif idx < 100:
		idx_3_digit = '0' + str(idx)
	else:
		idx_3_digit = str(idx)
	return idx_3_digit


args=get_args()
try:
	in_file = open(args.src_file, 'r')
	all_segments_4 = []
	all_segments_non_4 = []

	for utt in in_file:
		temp = utt.split('\t')
		idx = temp[0]
		votes = temp[1].split()

		votes_4 = []
		votes_non_4 = []

		subidx = 0
		start = 1
		end = 1
		prev_frame = '0'
		i = 1
		for curr_frame in votes:
			if curr_frame != prev_frame:
				if curr_frame == '4' and prev_frame != '4':
					if end-1 > 0:
						votes_non_4.append([subidx, start, end-1])
					start = i
					end = i
					subidx += 1
				elif curr_frame != '4' and prev_frame == '4':
					votes_4.append([subidx, start, end-1])
					start = i
					end = i
					subidx += 1

			elif i == len(votes): # handle the last segment
				if curr_frame == '4':
					votes_4.append([subidx, start, end])
				else:
					votes_non_4.append([subidx, start, end])
			
			prev_frame = curr_frame
			end += 1
			i += 1

		segments_4 = []
		segments_non_4 = []
		for segment in votes_4:
			idx_segment = idx + '_' + convert_to_3_digit(segment[0])
			segments_4.append([idx_segment, idx, segment[1], segment[2]])

		for segment in votes_non_4:
			idx_segment = idx + '_' + convert_to_3_digit(segment[0])
			segments_non_4.append([idx_segment, idx, segment[1], segment[2]])
		
		all_segments_4.extend(segments_4)
		all_segments_non_4.extend(segments_non_4)

	in_file.close()

	# write on the outdir
	try:
		# write the 'majority' file based on the frame idx
		out_file = open(args.dest_dir + '/segments_4_idx' + args.suffix + '.txt', 'w')
		for segment in all_segments_4:
			out_file.write(segment[0] + ' ' + segment[1] + ' ' + str(segment[2]) + ' ' + str(segment[3]) + '\n')
		out_file.close()
		print(">>>> " + len(all_segments_4) + " ('majority' segments) are exist")

		# write the non 'majority' file based on the frame idx
		out_file = open(args.dest_dir + '/segments_non_4_idx' + args.suffix + '.txt', 'w')
		for segment in all_segments_non_4:
			out_file.write(segment[0] + ' ' + segment[1] + ' ' + str(segment[2]) + ' ' + str(segment[3]) + '\n')
		out_file.close()
		print(">>>> " + len(all_segments_non_4) + " (non 'majority' segments) are exist")

	except Exception as e:
		raise e

except IOError as e:
	print("I/O error({0}): {1}".format(e.errno, e.strerror))


	