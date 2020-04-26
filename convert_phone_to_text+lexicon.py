# python convert_phone_to_text.py <src_file> <dest_file> <listwords-file>
# e.g. python convert_phone_to_text.py phone_segments_4_idx.txt text_segments_4_idx.txt lexicon.txt

import argparse

def get_args():
    """Get the input arguments from the stdin."""

    parser = argparse.ArgumentParser(description="Convert the phone segment to text.",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("phone_segment_file", type=str, metavar="the phone segment file")
    parser.add_argument("dest_file", type=str, metavar="destination file")
    parser.add_argument("listwords_file", type=str, metavar="listwords output file")
    
    return parser.parse_args()

if __name__ == '__main__':
	args = get_args()
	in_file = open(args.phone_segment_file, 'r')
	utts = []
	listwords = []
	for utt in in_file:
		temp = utt.split()
		frames = temp[2:]

		# # opsi 1 : setiap frame dianggap satu phone
		# segment = ''
		# for frame in frames:
		# 	if frame != '<sil>':
		# 		segment += frame.split('_')[0]
		# 	else:
		# 		segment += ' '

		# opsi 2 : frame yang punya phone sama, dianggap satu phone
		segment = ''
		prev = ''
		for curr in frames:
			if curr != prev:
				if curr != '<sil>':
					segment += curr.split('_')[0]
				else:
					segment += ' '
				prev = curr
		listwords.extend(segment.split())
		utts.append(temp[0] + ' ' + temp[1] + ' ' + segment + '\n')

	in_file.close()

	out_file = open(args.dest_file, 'w')
	for utt in utts:
		out_file.write(utt)
	out_file.close()


	# prepare the lexicon
	new_listwords = list(set(listwords))
	new_listwords.sort()
	
	out_file = open(args.listwords_file, 'w')
	for word in new_listwords:
		lex = ' '.join(word)
		out_file.write(word + ' ' + lex + '\n')
	out_file.close()