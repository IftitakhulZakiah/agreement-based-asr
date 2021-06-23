# convert the transition phone state (index) to phone state
# e.g. 50603 -> <noise>_S
# e.g. python state_to_phone.py transition_phone.txt ali.1.txt phones.1.txt

import sys

if __name__ == "__main__":
	transition_file = sys.argv[1]
	infile = sys.argv[2]
	outfile = sys.argv[3]
	
	file = open(transition_file, "r")
	phone_dict = [] # if transition-id = i (e.g. 100) then index of phone is i-1 (e.g. 99)
	temp_phone = ""
	# idx = 0
	for line in file:
		if "Transition-state" in line:
			temp_phone = line.split()[4]
		elif "Transition-id" in line:
			# idx = int(line.split(" ")[2])
			phone_dict.append(temp_phone)
	file.close()

	ali_file = open(infile, "r")
	temp_utt = ""
	phone_per_utt = {} # e.g. { "A013C001" : <sil> <sil> <sil> a_B , ...}
	for utt in ali_file:
		if utt != "\n":
			if (utt[0] != "#"):
				if ("show-alignments" not in utt):
					utt = utt.replace("[", "")
					utt = utt.replace("]", "")
					temp = utt.split()
					if temp[0] != temp_utt:
						temp_utt = temp[0]
						seq_phone = ""
						for i in range(1, len(temp)):
							seq_phone = seq_phone + " " + str(phone_dict[int(temp[i])-1])
						# print(seq_phone)
						phone_per_utt[temp_utt]	= seq_phone
	ali_file.close()

	sorted_phone_per_utt = [(k, phone_per_utt[k]) for k in sorted(phone_per_utt)]
	phone_file = open(outfile, "w")
	for utt in sorted_phone_per_utt:
		phone_file.write(utt[0] + "\t" + utt[1] + '\n')
	phone_file.close()
