import csv

new = []
csv.field_size_limit(10000000)
with open('results.csv') as f:
    reader = csv.reader(f)
    for row in reader:
        lines = row[0].split('\n')
        tmp = ''
        for i, line in enumerate(lines):
            tmp += ' ' + line
            if (i + 1) % 5 == 0:
                new.append((tmp, row[1]))
                tmp = ''
        new.append((tmp, row[1]))

with open('new_new.csv', 'w') as g:
    writer = csv.writer(g)
    for row in new:
        writer.writerow(row)