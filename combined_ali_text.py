
model='triphone'
with open( model + '/ali.all.txt', 'w') as outfile:
    for i in range(1,5):
        with open( model + '/ali.' + str(i) + '.txt') as infile:
            for line in infile:
                outfile.write(line)