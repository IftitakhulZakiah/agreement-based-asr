# python convert_phone_to_text.py <src_file> <dest_file> <listwords-file>
# e.g. python convert_phone_to_text.py phone_segments_idx.txt text_segments_idx.txt lexicon.txt

import argparse

def get_args():
    """Get the input arguments from the stdin."""

    parser = argparse.ArgumentParser(description="Convert the phone segment to text.",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("phone_segment_file", type=str, metavar="the phone segment file")
    parser.add_argument("dest_file", type=str, metavar="destination file")
    parser.add_argument("listwords_file", type=str, metavar="listwords output file")
    
    return parser.parse_args()

def search_key(in_dict, in_val):
	all_keys = list(in_dict.keys())
	for key in all_keys:
		curr_list = in_dict[key]
		if in_val in curr_list:
			return key
	return


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
		utts.append(temp[0] + ' ' + segment + '\n')

	in_file.close()

	out_file = open(args.dest_file, 'w')
	for utt in utts:
		out_file.write(utt)
	out_file.close()


	# prepare the lexicon
	new_listwords = list(set(listwords))
	new_listwords.sort()
	
	special_phones=['<napas>', '<batuk>', '<decak>', '<desis>', '<ketawa>', '<noise>', '<sil>']
	out_file = open(args.listwords_file, 'w')
	for word in new_listwords:

		spc_exist = {}
		substrings = []
		if any(spc in word for spc in special_phones):
			for special_phone in special_phones:
				temp_idxs = []
				for i in range(len(word)):
					temp_idx = word[i:].find(special_phone)
					temp_idxs.extend([temp_idx+i] if temp_idx != -1 else [])
				temp_idxs = list(set(temp_idxs))
				spc_exist[special_phone] = temp_idxs
			
			all_spc = list(spc_exist.keys())
			idxs = []
			for key in all_spc:
				idxs.extend(spc_exist[key])
			
			idx = -1
			curr_special_phone = ''
			for i in range(len(word)):
				if i in idxs:
					curr_special_phone = search_key(spc_exist, i)
					substrings.append(curr_special_phone)
					idx = i
				elif i < (idx+len(curr_special_phone)) and idx != -1:
					pass
				else:
					substrings.append(word[i])

			lex = ' '.join(substrings)
			print(lex)
		else:
			lex = ' '.join(word)
		
		out_file.write(word + ' ' + lex + '\n')
	out_file.close()
	print(">>>> Lexicon has been written")