# This script is to see the majority phone each frame based on the model alignment results
# e.g. python consensus.py --cnn-ali cnn_ali --lstm-ali lstm_ali tdnn_ali dnn_ali
# python consensus.py --cnn-ali cnn/ali.all.txt --lstm-ali lstm/ali.all.txt tdnn/ali.all.txt dnn/ali.all.txt

# python scripts/agreement-based-asr/consensus.py --cnn-ali /opt/kaldi/egs/asr_iif_/act_learning/exp/sample/mfcc_200128_no_oov/unlabeled/tri_ali_cnn/phone_ali/ali.all.txt --lstm-ali /opt/kaldi/egs/asr_iif_/act_learning/exp/sample/mfcc_200128_no_oov/unlabeled/tri_ali_lstm/phone_ali/ali.all.txt /opt/kaldi/egs/asr_iif_/act_learning/exp/sample/mfcc_200128_no_oov/unlabeled/tri_ali_tdnn/phone_ali/ali.all.txt /opt/kaldi/egs/asr_iif_/act_learning/exp/sample/mfcc_200128_no_oov/unlabeled/tri_ali_dnn/phone_ali/ali.all.txt 

import sys
import argparse
from collections import Counter

def get_args():
    """Get the input arguments from the stdin."""

    parser = argparse.ArgumentParser(description="Choose the majority frames.",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument("--cnn-ali", type=str, help="CNN alignment file")
    parser.add_argument("--lstm-ali", type=str, help="LSTM alignment file")
    parser.add_argument("tdnn_ali", type=str, metavar="<tdnn-ali>")
    parser.add_argument("dnn_ali", type=str, metavar="<dnn-ali>")
    
    return parser.parse_args()

def read_align_file(models):
	""" Args :: models -> array of path to align file """

	models_phone = {} # dict of dict with array as value
	for model in models:
		phones_temp = {}
		print(model)
		file_temp = open(model, 'r') # the ali.1.txt file
		for utt in file_temp:
			temp = utt.split('\t')
			phones_temp[temp[0]] = temp[1].split()

		file_temp.close()
		models_phone[model] = phones_temp

	return models_phone

# def is_model_exist(models_phone, model):
	""" Check in the models_phone, is the model exist? """


def rearrangement(models_phone, models):
	""" Rearrangement the models_phone
	 before : {'tdnn' : {utt1 : [tdnn_frame1, tdnn_frame2, ..], utt2 : ..., ...}, 
				'dnn' : {utt1 : [dnn_frame1, dnn_frame2, ..], utt2 : ..., ...}, ...}
	 # the utts_phone
	 after : {utt1 : {'frame1' : [tdnn_frame1, dnn_frame1, cnn_frame1, lstm_frame1],
						 'frame2' : [tdnn_frame2, dnn_frame2, cnn_frame2, lstm_frame2],
	 					...}...} """
	
	model_keys = list(models_phone.keys())
	is_cnn_exist = 0
	is_lstm_exist = 0

	if len(model_keys) >= 3:
		temp = [model_keys[2] for x in model_keys if 'cnn' in x]
		cnn_model_phone = temp[0] if len(temp) == 1 else 'not exist'
		is_cnn_exist = 1
		print('cnn model is exist ', cnn_model_phone)
	if len(model_keys) == 4:	
		temp = [model_keys[3] for x in model_keys if 'lstm' in x]
		lstm_model_phone = temp[0] if len(temp) == 1 else 'not exist'
		is_lstm_exist = 1
		print('lstm model is exist ', lstm_model_phone)

	tdnn_model_phone = model_keys[0] # tdnn model as reference
	dnn_model_phone = model_keys[1]
	
	utts_phone = {}
	for curr_utt in list(models_phone[tdnn_model_phone].keys()): 

		is_exist = 1
		is_has_same_n_frame = 0
		for model in models:
			if curr_utt not in models_phone[model]: # check is the utterance exist on each models?
				is_exist = 0

		if is_exist:
			n_frame_tdnn = len(models_phone[tdnn_model_phone][curr_utt])
			n_frame_dnn = len(models_phone[dnn_model_phone][curr_utt])
			n_frame_cnn = len(models_phone[cnn_model_phone][curr_utt]) if is_cnn_exist else 0
			n_frame_lstm = len(models_phone[lstm_model_phone][curr_utt]) if is_lstm_exist else 0

			# check is each utterance has same sum of frame?	
			if len(model_keys) >= 2:
				is_has_same_n_frame = 1 if n_frame_tdnn == n_frame_dnn else 0
			if len(model_keys) >= 3:
				is_has_same_n_frame = 1 if is_has_same_n_frame and (n_frame_tdnn == n_frame_cnn) else 0
			if len(model_keys) == 4:
				is_has_same_n_frame = 1 if is_has_same_n_frame and (n_frame_tdnn == n_frame_lstm) else 0

			if is_has_same_n_frame:
				utts_temp = {}
				# utts_temp = []
				counter_frame = 0
				for j in range(len(models_phone[tdnn_model_phone][curr_utt])): # total frame in curr_utt
					frame_temp = []
						# try:
					for model in models_phone:
						temp = models_phone[model][curr_utt][j]
						frame_temp.append(temp)
					utts_temp['frame' + str(counter_frame)] = frame_temp
					counter_frame += 1
				utts_phone[curr_utt] = utts_temp
			else:
				print(curr_utt + ' not exist on the all models or the models have different n frames')			
	
	# print(utts_phone)
	return utts_phone


def vote_per_frame(utts_phone):
	utts_frame_phones = {}
	utts_frame_count = {}

	utts_id = list(utts_phone.keys())

	n_1 = 0
	n_2 = 0
	n_3 = 0
	n_4 = 0
	for utt_id in utts_id:
		temp_utt = utts_phone[utt_id]
		frames_utt_temp = list(temp_utt.keys())

		frames_phone = ''
		frames_n = ''
		for frame_id in frames_utt_temp:
			temp_frame = temp_utt[frame_id]
			majority = get_max_majority(temp_frame)
			frames_phone = frames_phone + ' ' + majority[0]
			frames_n = frames_n + ' ' + str(majority[1])
			if majority[1] == 1:
				n_1 += 1
			elif majority[1] == 2:
				n_2 += 1
			elif majority[1] == 3:
				n_3 += 1
			elif majority[1] == 4:
				n_4 += 1

			# if majority[1] == 1:
			# 	print(utt_id, frame_id, majority[0])
			
		utts_frame_phones[utt_id] = frames_phone
		utts_frame_count[utt_id] = frames_n
		
	n_total = n_1 + n_2 + n_3 + n_4
	print('total vote 1 : ', n_1)
	print('total vote 2 : ', n_2)
	print('total vote 3 : ', n_3)
	print('total vote 4 : ', n_4)
	print('total frame : ', n_total)
	return utts_frame_phones, utts_frame_count

def get_max_majority(frame_phone_models):
	# frame_phone_models is array of phone from the models
	# e.g. ['<sil>', '<sil>', '<sil>']

	occurence_count = Counter(frame_phone_models)
	max_phone = occurence_count.most_common(1)[0]
	return max_phone


def write_file(utts_frame_phones, outfile):
	utts = list(utts_frame_phones.keys())

	file = open(outfile, 'w')
	for utt_id in utts:
		file.write(utt_id + '\t' + utts_frame_phones[utt_id] + '\n')
	file.close()
	return


if __name__ == '__main__':
	args = get_args()
	# for i in range(1,5):
	# 	cnn_phones = args.cnn_ali + '/phone_ali/ali.' + i + '.txt'
	# 	lstm_phones = args.lstm_ali + '/phone_ali/ali.' + i + '.txt'
	# 	dnn_phones = args.dnn_ali + '/phone_ali/ali.' + i + '.txt'
	# 	tdnn_phones = args.tdnn_ali + '/phone_ali/ali.' + i + '.txt'

	# urutan models harus tdnn, dnn, cnn, lstm
	models = [args.tdnn_ali, args.dnn_ali]	
	models_phone = read_align_file(models)
	utts_phone = rearrangement(models_phone, models)
	utts_frame_phones, utts_frame_count = vote_per_frame(utts_phone)
	write_file(utts_frame_phones, 'voting/phone_vote_consensus_tdnn.txt')
	write_file(utts_frame_count, 'voting/count_vote_consensus_tdnn.txt')