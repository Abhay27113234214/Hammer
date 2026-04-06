import csv
import os
import math
from minio import Minio 
from datetime import timedelta
import io

minio_client = Minio("127.0.0.1:9000", access_key="minioadmin", secret_key="minioadmin", secure=False)

def chunk_csv_manual(email, file_path, num_chunks):
    with open(file_path, 'r') as f:
        total_rows = sum(1 for _ in f) - 1

    num_chunks = min(total_rows, num_chunks)
    chunk_size = math.ceil(total_rows / num_chunks)
    ticket_urls = []

    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)

        for i in range(num_chunks):
            out_buffer = io.StringIO()
            writer = csv.writer(out_buffer)
            writer.writerow(header)

            for j in range(chunk_size):
                try:
                    writer.writerow(next(reader))
                except StopIteration:
                    break
            
            csv_bytes = out_buffer.getvalue().encode('utf-8')
            byte_stream = io.BytesIO(csv_bytes)

            chunk_name = f"{email}/chunk_{i}.csv"

            minio_client.put_object(
                bucket_name='hammer-data',
                object_name=chunk_name,
                data=byte_stream,
                length=len(csv_bytes),
                content_type='application/csv'
            )

            secure_url = minio_client.presigned_get_object(
                bucket_name='hammer-data',
                object_name=chunk_name,
                expires=timedelta(hours=3)
            )
            ticket_urls.append(secure_url)

    return ticket_urls