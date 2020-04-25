# convert the segment duration to utt2spk segment
# python convert_dur_to_utt2spk.py --copy_utt2spk 1 <dir>
# --- the <dir> have 'segments' file with format : segment_idx original_idx start_time end_time, e.g. A013C001_001 A013C001 0.07 0.10
# --- the start and end time are in second
# this script make 'utt2spk' based on utt2spk original 'utt2spk_ori'
# e.g. python convert_dur_to_utt2spk.py --copy_utt2spk 1 mfcc/train

import sys
import subprocess
import argparse

def get_args():
    """Get the input arguments from the stdin."""

    parser = argparse.ArgumentParser(description="Convert duration file to utt2spk.",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("--copy_utt2spk", type=bool, help="Is copy the original utt2spk?")
    parser.add_argument("datadir", type=str, metavar="<datadir>")
    
    return parser.parse_args()


if __name__ == '__main__':
	args = get_args()
	datadir = args.datadir
	is_copy = args.copy_utt2spk

	utt2spk_ori_file = open(datadir + '/utt2spk', 'r')
	for utt2spk in utt2spk_ori_file:
		spk_len = len(utt2spk.split()[1])
		rec_len = len(utt2spk.split()[0])
		break
	utt2spk_ori_file.close()

	in_file = open(datadir + '/segments', 'r')
	segments_spk = []
	segments_rec = []
	for segment in in_file:
		temp = segment.split()
		segments_spk.append(temp[0] + ' ' + temp[0][:spk_len] + '\n')
		segments_rec.append(temp[0] + ' ' + temp[0][:rec_len] + '\n')
	in_file.close()
	
	if is_copy:
		move_command = "mv " + datadir + "/utt2spk " + datadir + "/utt2spk_ori"
		process = subprocess.Popen(move_command.split(), stdout=subprocess.PIPE)
		output, error = process.communicate()
		print('The utt2spk ori is copied')

	out_file = open(datadir + '/utt2spk', 'w')
	for segment in segments_spk:
		out_file.write(segment)
	out_file.close()

	out_file = open(datadir + '/utt2rec', 'w')
	for segment in segments_rec:
		out_file.write(segment)
	out_file.close()