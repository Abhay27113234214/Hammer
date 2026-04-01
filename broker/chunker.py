import csv
import os
import math

basedir=os.path.abspath(os.path.dirname(__file__))
root_dir = os.path.abspath(os.path.join(basedir, '..'))

CHUNKS_FOLDER = os.path.join(root_dir, "chunks")

def chunk_csv_manual(file_path, num_chunks):
    os.makedirs(CHUNKS_FOLDER, exist_ok=True)
    with open(file_path, 'r') as f:
        total_rows = sum(1 for _ in f) - 1

    num_chunks = min(total_rows, num_chunks)

    chunk_size = math.ceil(total_rows / num_chunks)

    with open(file_path, 'r') as f:
        reader = csv.reader(f)
        header = next(reader)

        for i in range(num_chunks):
            with open(os.path.join(CHUNKS_FOLDER,f'chunk_{i}.csv'), 'w', newline='') as out:
                writer = csv.writer(out)
                writer.writerow(header)
                for _ in range(chunk_size):
                    try:
                        writer.writerow(next(reader))
                    except StopIteration:
                        break