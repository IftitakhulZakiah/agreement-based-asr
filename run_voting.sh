#!/bin/bash
set -e 

[ -f path.sh ] && . ./path.sh # source the path.
. parse_options.sh || exit 1;

nj=20

cmd=utils/parallel/run.pl
date=200128


feat_type=fbank
unlabeled_with_label_feat=${feat_type}/sample_${date}/unlabeled_with_labelv2
unlabeled_feat=${feat_type}/sample_${date}/unlabeled
labeled_feat=${feat_type}/sample_${date}/labeled
labeled_unlabeled_with_label=$(dirname $labeled_feat)/labeled_unlabeled_with_label
test_feat=${feat_type}/sample_${date}/testv2

train_dict=data/local/dict-train-${date}-psv2
train_lang=data/lang-train-${date}-psv2
temp_dir=data/local/temp

curr_model=tdnn_fbank_pitch
model_decode=exp/sample/mfcc_${date}_psv2/${curr_model}/lstm4f
# model_decode=/raid/speech/asr_iif_/act_learning/exp/sample/nnet3_psv2/${curr_model}
decode_unlabeled_dir=$model_decode/"decode_$(basename $unlabeled_with_label_feat)_informal_lexv2"


# prepare dir from predicted
unlabeled_predicted_feat=$(dirname ${unlabeled_feat})/unlabeled_predicted_psv2/${curr_model}
# combined_feat=$(dirname ${unlabeled_feat})/combined/tri_mixed
# run_prepare_predicted=false
# if [ $run_prepare_predicted = true ];
# then
# 	echo ""
# 	echo ">> Prepare dir from predicted label . . ."
# 	echo "$decode_unlabeled_dir"
# 	python scripts/agreement-based-asr/decode_to_text.py $decode_unlabeled_dir $unlabeled_feat $unlabel_predicted_feat
# 	steps/compute_cmvn_stats.sh $unlabeled_predicted_feat || exit 1;
# fi

# align the decode result
acm_tri=exp/sample/mfcc_${date}_psv2/tri_psv2
modelali=$(dirname ${acm_tri})/unlabeled_ali/tri_ali_${curr_model}
# run_align_decode=false
# if [ $run_align_decode = true ]; 
# then
# 	echo ""
# 	echo ">> Alignment at $unlabeled_feat"
# 	steps/align_si.sh $unlabeled_predicted_feat $train_lang $acm_tri $modelali || exit 1;
# fi


modelali=exp/sample/mfcc_200128_psv2/labeled_unlabeled_aliv2/tdnn_fbank_pitch_iter1.6_sp
# modelali=exp/sample/mfcc_200128_psv2/unlabeled_ali/tri_ali_tdnn_fbank_pitch_iter1.6_sp/
nj=4
run_show_alignment=true
if [ $run_show_alignment = true ];
then
	echo ""
	echo ">> Show readible alignment $modelali on $modelali/txt/"
	$cmd JOB=1:$nj $modelali/state_ali/ali.JOB.txt \
		show-alignments $train_lang/phones.txt $modelali/final.mdl "ark:gunzip -c -k $modelali/ali.JOB.gz|" || exit 1;
	show-transitions $train_lang/phones.txt $modelali/final.mdl > $modelali/state_ali/transitions_phone.txt
fi

run_convert_state_to_phones=true
if [ $run_convert_state_to_phones = true ];
then
	echo ""
	echo ">> Convert state to phoneme"
							# $cmd JOB=1:$nj $modelali/phones_ali/ali.JOB.txt \
							# 	ali-to-phones --per-frame $modelali/final.mdl "ark:gunzip -c -k $modelali/ali.JOB.gz|" "ark:-\n" || exit 1;
	mkdir -p $modelali/phone_ali/
	i=1
	while [ $i -le $nj ];do
		python scripts/agreement-based-asr/state_to_phone.py $modelali/state_ali/transitions_phone.txt \
			$modelali/state_ali/ali.${i}.txt $modelali/phone_ali/ali.${i}.txt 
		((i++))
	done
	python scripts/agreement-based-asr/merge_text.py $modelali/phone_ali/
fi


run_frame_shift=false
if [ $run_frame_shift = true ];
then
	echo ""
	echo ">> Get the frame shift"
	utils/data/get_frame_shift.sh $unlabeled_with_label_feat
	utils/data/get_utt2num_frames.sh $unlabeled_with_label_feat
	# utils/data/get_utt2dur.sh $unlabeled_with_label_feat
	# utils/data/get_segments_for_data.sh $unlabeled_with_label_feat > $unlabeled_with_label_feat/segments
fi


modelali=exp/sample/mfcc_200128_psv2/unlabeled_ali/
vote_dir=voting/psv2_model_tdnnv2.1/ 
run_consensus=false
if [ $run_consensus = true ];then
	# i=1
	# nj=20
	# while [ $i -le $nj ];do
		modelali_dnn=$modelali/tri_ali_dnn/phone_ali/ali.all.txt
		modelali_lstm=$modelali/tri_ali_lstm_hires/phone_ali/ali.all.txt
		modelali_cnn=$modelali/tri_ali_cnn/phone_ali/ali.all.txt
		modelali_tdnn=$modelali/tri_ali_tdnn_fbank_pitch/phone_ali/ali.all.txt

		mkdir -p $vote_dir
		python scripts/agreement-based-asr/consensus.py --cnn-ali $modelali_cnn --lstm-ali $modelali_lstm \
			$modelali_tdnn $modelali_dnn $vote_dir || exit 1;
	# 	((i++))
	# done
fi


frame_shift=10
frame_dur=25
suffix=''
run_split_majority=false
if [ $run_split_majority = true ];
then
	echo ""
	echo ">> Split the 'majority' segments and not"
	python scripts/agreement-based-asr/split_4_and_not_text.py $vote_dir/count_vote.txt $vote_dir/phone_vote.txt $vote_dir

	mkdir -p $vote_dir/full_vote
	mkdir -p $vote_dir/no_full_vote
	mv ${vote_dir}/segments_4_idx.txt "$vote_dir/full_vote/segments_idx${suffix}.txt"
	mv ${vote_dir}/segments_non_4_idx.txt "$vote_dir/no_full_vote/segments_idx${suffix}.txt"

	python scripts/agreement-based-asr/convert_segment_to_dur.py "$vote_dir/full_vote/segments_idx${suffix}.txt" \
		"$vote_dir/full_vote/segments_dur${suffix}.txt" $frame_dur $frame_shift 

	python scripts/agreement-based-asr/convert_segment_to_dur.py "$vote_dir/no_full_vote/segments_idx${suffix}.txt" \
		"$vote_dir/no_full_vote/segments_dur${suffix}.txt" $frame_dur $frame_shift 

	mv ${vote_dir}/phone_segments_4_idx.txt "$vote_dir/full_vote/phone_segments_idx${suffix}.txt"
	mv ${vote_dir}/phone_segments_non_4_idx.txt "$vote_dir/no_full_vote/phone_segments_idx${suffix}.txt"

	echo "The split file already created"
fi


vote_dir=${vote_dir}/full_vote/
unlabeled_with_label_feat=${feat_type}/sample_${date}/unlabeled_with_labelv2
vote_feat=$(dirname $unlabeled_with_label_feat)/unlabeled_full_iter1.5
run_extract_segment=false
if [ $run_extract_segment = true ];then

	# nsegment=$(wc -l < $vote_dir/segments_dur${suffix}.txt)
	# # nsegment=2
	# # rm $vote_dir/segments_dur${suffix}-sp09.txt
	# for ((i=1; i<=nsegment; i++));do
	# 	utt=$(awk -v "i=$i" 'NR==i {print "sp0.9-"$1,"sp0.9-"$2,$3,$4}' $vote_dir/segments_dur${suffix}.txt)
	# 	echo $utt >>$vote_dir/segments_dur${suffix}-sp09.txt
	# 	echo $utt
	# done

	####################################################################
	# infile=$vote_dir/phone_segments_idx${suffix}.txt
	# outfile=$vote_dir/phone_segments_idx${suffix}_sp10.txt

	# mkdir -p $(dirname $outfile)

	# nj=2
	# for i in `seq $nj`; 
	# do(
	# 	split -n l/$i/$nj $infile > $(dirname $infile)/${i}.txt
	# 	python scripts/agreement-based-asr/create_speed_perturb.py $(dirname $infile)/${i}.txt $(dirname $outfile)/${i}.txt
	# )&
	# done

	# cat $(dirname $infile)/1.txt $(dirname $infile)/2.txt > $outfile
	# 		### cat ${outfile/'11'/'09'} ${outfile/'11'/'10'} ${outfile} > ${outfile/'11'/''}
	# rm $(dirname $infile)/1.txt 
	# rm $(dirname $infile)/2.txt

	####################################################################

	mkdir -p $vote_feat
			# cp -r "$vote_dir/segments_dur${suffix}.txt" ${unlabeled_with_label_feat}/segments
			# utils/data/extract_wav_segments_data_dir.sh $unlabeled_with_label_feat $vote_feat
	utils/data/subsegment_data_dir.sh $unlabeled_with_label_feat $vote_dir/segments_dur${suffix}.txt $vote_feat

			cp -r "$vote_dir/segments_dur${suffix}.txt" ${vote_feat}/segments
	python scripts/agreement-based-asr/convert_dur_to_utt2spk.py --copy_utt2spk 1 $vote_feat
	python scripts/agreement-based-asr/convert_phone_to_text+lexicon.py ${vote_dir}/phone_segments_idx.txt \
		$vote_feat/text ${vote_feat}/lexicon.txt

	steps/compute_cmvn_stats.sh $vote_feat
	utils/fix_data_dir_segment.sh $vote_feat
fi

suffix=psv2-combine_iter1.6
vote_dict=data/local/dict-train-${date}-${suffix}
vote_lang=data/lang-train-${date}-${suffix}
prepare_vote_lang=false
if [ $prepare_vote_lang = true ];
then
	echo ""
	echo ">> Create lang for training from $vote_dict to $vote_lang"
	mkdir -p $vote_dict
	cp -r $train_dict/nonsilence_phones.txt $vote_dict/
	cp -r $train_dict/optional_silence.txt $vote_dict/
	cp -r $train_dict/silence_phones.txt $vote_dict/

	# ## Digunakan jika ingin memisahkan dict hasil iterasi dan dict asli untuk training
	# cp -r ${vote_feat}/lexicon.txt $vote_dict/lexicon.txt
	# sed -i '1 i\<unk> <noise>' $vote_dict/lexicon.txt
	# rm ${vote_feat}/lexicon.txt

	# Digunakan jika ingin menggabungkan dict hasil iterasi dan dict asli untuk training
	cp -r $train_dict/lexicon.txt $vote_dict/lexicon_ori.txt
	cp -r ${vote_dict/'combine'/'full'}/lexicon.txt $vote_dict/lexicon_vote.txt
			# cp -r ${vote_feat}/lexicon.txt $vote_dict/lexicon_vote.txt
			# rm ${vote_feat}/lexicon.txt
	cat $vote_dict/lexicon_ori.txt $vote_dict/lexicon_vote.txt | sort -u > $vote_dict/lexicon.txt
	rm $vote_dict/{lexicon_ori.txt,lexicon_vote.txt}

	utils/prepare_lang.sh $vote_dict "<unk>" $temp_dir $vote_lang || exit 1;
fi


feat_type=fbank
suffix='_sp'
combined_data=${feat_type}/sample_${date}/labeled_unlabeled_full_iter1.6${suffix}
data1=${feat_type}/sample_${date}/labeled${suffix}
data2=${feat_type}/sample_${date}/unlabeled_full_iter1.6${suffix}
modelali1=exp/sample/mfcc_200128_psv2/tri_psv2_ali_labeled${suffix}
modelali2=exp/sample/mfcc_200128_psv2/unlabeled_ali/tri_ali_tdnn_fbank_pitch_iter1.6${suffix}
combined_ali=exp/sample/mfcc_200128_psv2/labeled_unlabeled_aliv2/tdnn_fbank_pitch_iter1.6${suffix}
run_combine_ali=false
if [ $run_combine_ali = true ];then
	# utils/data/modify_speaker_info.sh --utts-per-spk-max 2 $data2 ${data2}_max2
	# utils/combine_data_segment.sh ${combined_data} ${data1} ${data2}
	steps/combine_ali_dirs.sh $combined_data $combined_ali $modelali1 $modelali2
fi