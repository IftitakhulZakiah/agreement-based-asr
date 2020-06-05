# e.g. python calculate_phone.py ..\align-result\tdnn-iter1.3\ali.all.txt ..\align-result\tdnn-iter1.3\ali.phones.txt 

import argparse

def get_args():
    """Get the input arguments from the stdin."""

    parser = argparse.ArgumentParser(description="Calculate the phones.",
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("ali_file", type=str, metavar="input file that formatted as like the output of state_to_phone.py")
    parser.add_argument("out_file", type=str, metavar="output file")
    
    return parser.parse_args()

def write_file(path, input_phones):
	file = open(path, 'w')
	for phone in input_phones:
		file.write(phone[0] + '\t' + str(phone[1]) + '\n')
	file.close()


def calculate_segment_phones(path):
	phones = {}
	file = open(path, 'r')
	for line in file:
		temp = line.split()
		if '_' in temp[0]: #get the segment only based on the idx
			for i in range(1,len(temp)):
				if temp[i] in phones.keys():
					phones[temp[i]] += 1
				else:
					phones[temp[i]] = 1

	file.close()
	sorted_phones = sorted(phones.items(), key=lambda kv:(kv[1], kv[0]), reverse=True)
	return sorted_phones

if __name__ == '__main__':
	args = get_args()
	phones = calculate_segment_phones(args.ali_file)
	write_file(args.out_file, phones)