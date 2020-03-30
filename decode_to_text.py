# convert the decode result to text per utterance and linking the utt2spk & wav.scp to <dest_dir> from <source_dir>
# python decode_to_text.py <decode_dir> <source_dir> <dest_dir> 
# e.g. python decode_to_text.py exp/tri/decode_unlabeled mfcc/unlabeled mfcc/unlabeled_act_learn

# <decode_dir> : the decode directory
# <source_dir> : the feature directory that decoded on <decode_dir>
# <dest_dir> : the new feature directory

import sys
import re
import os

if __name__ == '__main__':
	decode_dir = sys.argv[1]
	source_dir = sys.argv[2]
	dest_dir = sys.argv[3]
	in_file_path = decode_dir + '/scoring_kaldi/wer_details/per_utt'

	utts = []
	in_file = open(in_file_path, 'r')
	i = 0
	for line in in_file:
		if (i % 4 == 1): # take hyp only
			idx = line.split()[0]
			hyp = re.sub(' +', ' ', line)
			sentence = hyp.split(' ',2)[2]
			sentence = sentence.replace('***', '')
			utts.append(idx + ' ' + sentence)
		i += 1
	in_file.close()

	os.system('mkdir ' + dest_dir ) # Todo : check if it's already exist, skip
	out_file_path = dest_dir + '/text'
	out_file = open(out_file_path , 'w')
	for utt in utts:
		out_file.write(utt)
	out_file.close()

	os.system('echo ">>>> Text already written"')
	os.system('cp -r ' + source_dir + '/utt2spk ' + dest_dir)
	os.system('cp -r ' + source_dir + '/spk2utt ' + dest_dir)
	os.system('cp -r ' + source_dir + '/wav.scp ' + dest_dir)
	os.system('cp -r ' + source_dir + '/feats.scp ' + dest_dir)