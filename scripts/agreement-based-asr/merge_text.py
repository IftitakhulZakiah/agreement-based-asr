# merge all files in the directory and write down as "ali.all.txt" in the same dir
# python merge_text.py <dir>
# e.g. python merge_text.py exp/tri_ali/phones_ali/

# python scripts/agreement-based-asr/merge_text.py \
#  		/opt/kaldi/egs/asr_iif_/act_learning/exp/sample/mfcc_200128_no_oov/unlabeled/tri_ali_tdnn/phone_ali/


import os
import sys

curr_dir = sys.argv[1]

filenames = []
path = ''
for root, _, files in os.walk(curr_dir, topdown = False):
	filenames = files
	path = root

with open( curr_dir + '/ali.all.txt', 'w') as outfile:
    for i in range(1,len(filenames)):
        with open( curr_dir + '/ali.' + str(i) + '.txt') as infile:
            for line in infile:
                outfile.write(line)
