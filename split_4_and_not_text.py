# split the 'majority' (4) segment and not 'majority'
# python split_4_and_not_text.py <count_file> <phone_file> <dest_dir>
# e.g. python split_4_and_not.py count_vote.txt phone_vote.txt segments/

import sys
import argparse

def get_args():
    """Get the input arguments from the stdin."""

    parser = argparse.ArgumentParser(description="Split the majority segments.",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("--suffix", type=str, help="suffix for the out file")
    parser.add_argument("count_file", type=str, metavar="count the voting file")
    parser.add_argument("phone_file", type=str, metavar="phone the voting file")
    parser.add_argument("dest_dir", type=str, metavar="destination directory")
    
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
	phone_files = []
	phone_file = open(args.phone_file, 'r')
	for utt in phone_file:
		phone_files.append(utt)
	phone_file.close()

	in_file = open(args.count_file, 'r')
	all_segments_4 = []
	all_segments_non_4 = []
	all_phones_4 = []
	all_phones_non_4 = []
	j = 0
	for utt in in_file:
		temp = utt.split('\t')
		idx = temp[0]
		votes = temp[1].split()
		phones = phone_files[j].split('\t')[1].split()
		
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
		phone_segments_4 = []
		phone_segments_non_4 = []
		for segment in votes_4:
			idx_segment = idx + '_' + convert_to_3_digit(segment[0])
			segments_4.append([idx_segment, idx, str(segment[1]), str(segment[2])])
			# concatenate the phones in a segment
			temp = phones[segment[1]-1:segment[2]]
			phone_segments_4.append([idx_segment, idx, ' '.join(temp)])

		for segment in votes_non_4:
			idx_segment = idx + '_' + convert_to_3_digit(segment[0])
			segments_non_4.append([idx_segment, idx, str(segment[1]), str(segment[2])])
			# concatenate the phones in a segment
			temp = phones[segment[1]-1:segment[2]]
			phone_segments_non_4.append([idx_segment, idx, ' '.join(temp)])

		all_segments_4.extend(segments_4)
		all_segments_non_4.extend(segments_non_4)
		all_phones_4.extend(phone_segments_4)
		all_phones_non_4.extend(phone_segments_non_4)

		j += 1
	in_file.close()

	# write on the outdir
	try:
		write_items = [all_segments_4, all_phones_4, all_segments_non_4, all_phones_non_4]
		filenames = ['/segments_4_idx', '/phone_segments_4_idx', '/segments_non_4_idx', '/phone_segments_non_4_idx' ]

		# write the 'majority' file based on the frame idx
		for i in range(len(write_items)):
			suffix = args.suffix if args.suffix is not None else ''
			out_file = open(args.dest_dir + filenames[i] + suffix + '.txt', 'w')
			for segment in write_items[i]:
				temp = ' '.join(segment)
				out_file.write(temp + '\n')
			out_file.close()
			print(">>>> " + str(len(write_items[i])) + " " + filenames[i].replace('/','') + " already written")

	except Exception as e:
		raise e

except IOError as e:
	print("I/O error({0}): {1}".format(e.errno, e.strerror))


	