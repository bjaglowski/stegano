import subprocess

IMAGES = ('Sample-png-image-100kb.png', 'Sample-png-image-1MB.png', 'Sample-png-image-10MB.png')
GENERATORS = ('fibonacci', 'eratosthenes', 'identity', 'triangular_numbers', 'composite', 'carmichael', 'log_gen')
MESSAGES = ('S', 'Sekret', 'Bardzo, bardzo duzy sekret. Na prawde dlugi. Dluzszy niz poprzednie.. na pewno',
            'Lorem ipsum dolor sit amet, consectetur adipiscing elit.Morbi accumsan mollis felis id hendrerit.Aenean '
            'hendrerit placerat fermentum.Vivamus vel risus euismod, dapibus erat eu, laoreet leo.Vivamus at ipsum a '
            'nisi commodo suscipit eu eget neque.Nunc fringilla sagittis blandit.Nunc tincidunt nisl ullamcorper '
            'scelerisque accumsan.Phasellus eu arcu ac dolor malesuada imperdiet.Quisque hendrerit tellus nisl, '
            'ut mattis tellus pharetra quis.Aliquam ut purus eget sem pulvinar rhoncus eu vitae ex.Sed aliquet leo ut '
            'leo facilisis, nec faucibus odio faucibus.Nam vitae augue in lectus venenatis sollicitudin id in velit.')
OUT_FILE = 'out.png'
RESULTS_FILE = 'results.csv'


import csv
import os
import time

from itertools import product

if os.path.exists(OUT_FILE):
    os.remove(OUT_FILE)

if os.path.exists(RESULTS_FILE):
    os.remove(RESULTS_FILE)

with open(RESULTS_FILE, 'w', encoding='utf-8', newline='') as results:
    writer = csv.writer(results)
    writer.writerow(['generator', 'image', 'message', 'org_size', 'out_size', 'hide_time', 'reveal_size'])

    for image, generator, message in product(IMAGES, GENERATORS, MESSAGES):

        org_size = os.path.getsize(image)
        hide_t = time.time()
        sub = subprocess.run(['python', 'hide.py', 'hide', '-s', image, '-d', OUT_FILE, '-g', generator, message], stdout=subprocess.DEVNULL)
        hide_t = time.time() - hide_t
        if sub.returncode:
            print('Hide error running: ', generator)
            writer.writerow([generator, image, message, org_size, None, None, None])
            continue

        size = os.path.getsize(OUT_FILE)

        reveal_t = time.time()
        sub = subprocess.run(['python', 'hide.py', 'reveal', OUT_FILE, '-g', generator], stdout=subprocess.DEVNULL)
        reveal_t = time.time() - reveal_t

        if sub.returncode:
            print('Reveal error running: ', generator)
            continue

        print(f'Generator: {generator}, image: {image}, hide_time: {hide_t}, reveal_time: {reveal_t}, file_size: {size}, diff: {(size - org_size) / org_size * 100:.04f}, message: "{message}"')
        writer.writerow([generator, image, org_size, size, hide_t, reveal_t, message])
        if os.path.exists(OUT_FILE):
            os.remove(OUT_FILE)
