#!/bin/bash
clear

[ -f path.sh ] && . ./path.sh # source the path.
. parse_options.sh || exit 1;

nj=30

cmd=utils/parallel/run.pl
date=200128

# extract feature
feat_type=mfcc		
feat_conf=conf/${feat_type}.conf
unlabeled_with_label_feat=${feat_type}/sample_${date}/unlabeled_with_label
unlabeled_feat=${feat_type}/sample_${date}/unlabeled
labeled_feat=${feat_type}/sample_${date}/labeled
test_feat=${feat_type}/sample_${date}/test

run_feat_extraction=false
if [ $run_feat_extraction = true ];
then
	echo ""
	echo ">> Extract feature with $feat_type at $unlabeled_feat"
	utils/fix_data_dir.sh $unlabeled_feat || exit 1;
	steps/make_mfcc.sh --nj $nj --mfcc-config $feat_conf $unlabeled_feat \
		${unlabeled_feat}/data/log ${unlabeled_feat}/data || exit 1;
	steps/compute_cmvn_stats.sh $unlabeled_feat || exit 1;

	# echo ""
	# echo ">> Extract feature with $feat_type at $labeled_feat"
	# utils/fix_data_dir.sh $labeled_feat || exit 1;
	# steps/make_mfcc.sh --nj $nj --mfcc-config $feat_conf $labeled_feat \
	# 	${labeled_feat}/data/log ${labeled_feat}/data || exit 1;
	# steps/compute_cmvn_stats.sh $labeled_feat || exit 1;

	# echo ""
	# echo ">> Extract feature with $feat_type at $test_feat"
	# utils/fix_data_dir.sh $test_feat || exit 1;
	# steps/make_mfcc.sh --nj $nj --mfcc-config $feat_conf $test_feat \
	# 	${test_feat}/data/log ${test_feat}/data || exit 1;
	# steps/compute_cmvn_stats.sh $test_feat || exit 1;

	# echo ""
	# echo ">> Combine data adapt $adapt_feat and data train $gaib_feat"
	# utils/combine_data.sh $labeled_feat $adapt_feat $gaib_feat || exit 1;
else
	echo ""
	echo ">> Skip feature extraction..."
fi


# split data for cross-val
nsplit=10
split_data=false
if [ $split_data = true ];
then
	echo ""
	echo ">> Split the $adapt_feat becomes $nsplit"
	split_data_dir.sh $adapt_feat $nsplit
else
	echo ""
	echo ">> Skip split data..."
fi


# create training lang
train_dict=data/local/dict-train-${date}-no-oov
train_lang=data/lang-train-${date}-no-oov
temp_dir=data/local/temp
run_prepare_train_lang=false
if [ $run_prepare_train_lang = true ];
then
	echo ""
	echo ">> Create lang for training from $train_dict to $train_lang"
	utils/prepare_lang.sh $train_dict "<unk>" $temp_dir $train_lang || exit 1;
else
	echo ""
	echo ">> Skip lang train preparation..."
fi

# train monophone
acm_mono=exp/sample/mfcc_${date}_no_oov/mono
run_train_mono=false
if [ $run_train_mono = true ];
then
	echo ""
	echo ">> Train monophone at $acm_mono"
	steps/train_mono.sh --nj $nj --cmd $cmd $labeled_feat $train_lang $acm_mono || exit 1;
else
	echo ""
	echo ">> Skip train acm mono..."
fi

# train triphone
num_leaf=10000
num_gaus=200000
acm_tri=exp/sample/mfcc_${date}_no_oov/tri
mono_ali=exp/sample/mfcc_${date}_no_oov/mono_ali
run_train_tri=false
if [ $run_train_tri = true ];
then
	echo ""
	echo ">> Train triphone at $acm_tri"
	steps/align_si.sh --nj $nj --cmd $cmd $labeled_feat $train_lang $acm_mono \
		$mono_ali || exit 1;
	steps/train_deltas.sh $num_leaf $num_gaus $labeled_feat $train_lang \
		$mono_ali $acm_tri || exit 1;
else
	echo ""
	echo ">> Skip train acm tri..."
fi


# create test lang
test_dict=$train_dict
test_lang=$(dirname $train_lang)/lang-test-gabungan-${date}
lm_dir=/opt/kaldi/egs/asr_iif_/act_learning/data/local/lm/sample_${date}_no_oov/trigram_sample_${date}_no_oov.arpa
run_prepare_test_lang=false
if [ $run_prepare_test_lang = true ];
then
	echo ""
	echo ">> Create lang for test from $test_dict to $test_lang"
	utils/prepare_lang.sh $test_dict "<unk>" $temp_dir $test_lang || exit 1;
	# /opt/kaldi/src/lmbin/arpa2fst $lm_dir | fstprint | utils/eps2disambig.pl | utils/s2eps.pl | fstcompile \
	# 	--isymbols=${test_lang}/words.txt --osymbols=${test_lang}/words.txt \
	# 	--keep_isymbols=false --keep_osymbols=false | fstrmepsilon | fstarcsort \
	# 	--sort_type=ilabel > ${test_lang}/G.fst

	/opt/kaldi/src/lmbin/arpa2fst --disambig-symbol=#0 --read-symbol-table=${test_lang}/words.txt $lm_dir ${test_lang}/G.fst 
else
	echo ""
	echo ">> Skip lang test preparation..."
fi



# make graph
model_decode=${acm_tri}
graph_dir=${model_decode}/graph_sample_${date}
run_make_graph=false
if [ $run_make_graph = true ];
then
	echo ""
	echo ">> Create graph at $graph_dir"
	utils/mkgraph.sh --remove-oov $test_lang $acm_tri $graph_dir
else
	echo ""
	echo ">> Skip make graph..."
fi

# decode
decode_dir=${model_decode}/"decode_sample_$(basename $test_feat)_${date}"
# decode_unlabeled_dir=$(dirname $acm_tri)/nnet_sample_${date}/dbn_dnn_labeled/"decode_$(basename $unlabeled_feat)_${date}"
decode_unlabeled_dir=$model_decode/"decode_$(basename $unlabeled_with_label_feat)_${date}"
run_decode=false
if [ $run_decode = true ];
then
	echo ""
	echo ">> Decoding at $test_feat"
	steps/decode.sh --nj $nj ${graph_dir} $test_feat ${decode_dir}
	echo ""
	echo ">> Decoding at $unlabeled_with_label_feat"
	steps/decode.sh --nj $nj ${graph_dir} $unlabeled_with_label_feat ${decode_unlabeled_dir}
else
	echo ""
	echo ">> Skip decoding. . ."
fi


# prepare dir from predicted
nj=20
unlabeled_predicted_feat=$(dirname ${unlabeled_feat})/unlabeled_predicted_no_oov_model/tri
# combined_feat=$(dirname ${unlabeled_feat})/combined/tri_mixed
run_prepare_predicted=false
if [ $run_prepare_predicted = true ];
then
	echo ""
	echo ">> Prepare dir from predicted label . . ."
	echo "$decode_unlabeled_dir"
	python decode_to_text.py $decode_unlabeled_dir $unlabeled_feat $unlabel_predicted_feat
	steps/compute_cmvn_stats.sh $unlabeled_predicted_feat || exit 1;
else
	echo ""
	echo ">> Skip prepare dir from predicted label. . ."
fi

# align the decode result
modelali=$(dirname ${acm_tri})/unlabeled/tri_ali_lstm
run_align_decode=false
if [ $run_align_decode = true ]; 
then
	echo ""
	echo ">> Alignment at $unlabeled_feat"
	steps/align_si.sh $unlabeled_predicted_feat $train_lang $acm_tri $modelali || exit 1;
else
	echo ""
	echo ">> Skip alignment result. . ."
fi

# utils/combine_data.sh $combined_feat $labeled_feat $unlabel_predicted_feat

modelali=exp/sample/mfcc_200128_no_oov/unlabeled/tri_ali_dnn
nj=4
run_show_alignment=true
if [ $run_show_alignment = true ];
then
	echo ""
	echo ">> Show readible alignment $modelali on $modelali/txt/"
	$cmd JOB=1:$nj $modelali/state_ali/ali.JOB.txt \
		show-alignments $train_lang/phones.txt $modelali/final.mdl "ark:gunzip -c -k $modelali/ali.JOB.gz|" || exit 1;
	show-transitions $train_lang/phones.txt $modelali/final.mdl > $modelali/state_ali/transitions_phone.txt
else 
	echo ""
	echo ">> Skip show alignment. . ."
fi

run_convert_state_to_phones=true
if [ $run_convert_state_to_phones = true ];
then
	echo ""
	echo ">> Convert state to phoneme"
	# $cmd JOB=1:$nj $modelali/phones_ali/ali.JOB.txt \
	# 	ali-to-phones --per-frame $modelali/final.mdl "ark:gunzip -c -k $modelali/ali.JOB.gz|" "ark:-\n" || exit 1;
	mkdir $modelali/phone_ali/
	i=1
	while [ $i -le $nj ]
	do
		python state_to_phone.py $modelali/state_ali/transitions_phone.txt \
			$modelali/state_ali/ali.${i}.txt $modelali/phone_ali/ali.${i}.txt 
		((i++))
	done
else 
	echo ""
	echo ">> Skip convert to phoneme. . ."
fi