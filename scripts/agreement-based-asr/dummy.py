def search_key(in_dict, in_val):
	all_keys = list(in_dict.keys())
	for key in all_keys:
		curr_list = in_dict[key]
		if in_val in curr_list:
			return key
	return


if __name__ == '__main__':
	# temp = "<napas>ae<napas>"
	temp = "<decakk>ae<napas>hik<ss>s<decakk>"
	special_phones = ["<napas>", "<decakk>", "<ss>"]

	spc_exist = {}
	substrings = []
	if any(spc in temp for spc in special_phones):
		for special_phone in special_phones:
			temp_idxs = []
			for i in range(len(temp)):
				temp_idx = temp[i:].find(special_phone)
				temp_idxs.extend([temp_idx+i] if temp_idx != -1 else [])
			temp_idxs = list(set(temp_idxs))
			spc_exist[special_phone] = temp_idxs
		
		all_spc = list(spc_exist.keys())
		idxs = []
		for key in all_spc:
			idxs.extend(spc_exist[key])
		
		idx = -1
		curr_special_phone = ''
		for i in range(len(temp)):
			if i in idxs:
				curr_special_phone = search_key(spc_exist, i)
				substrings.append(curr_special_phone)
				idx = i
			elif i < (idx+len(curr_special_phone)) and idx != -1:
				pass
			else:
				substrings.append(temp[i])

		lex = ' '.join(substrings)
		print(lex)

