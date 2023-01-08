from hashlib import md5

def file_md5_hash(filename):
    with open(filename, "rb") as f:
        return md5(f.read()).hexdigest()