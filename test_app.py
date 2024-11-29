
import os
import threading
import time
import filecmp
from app import send_file, receive_file

def create_test_file(path, content="This is a test file content"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        f.write(content)

def test_file_transfer():
    test_dir = "test_files"
    os.makedirs(test_dir, exist_ok=True)
    
    source_file = os.path.join(test_dir, "source.txt")
    received_file = os.path.join(test_dir, "received.txt")
    create_test_file(source_file)
    
    receiver_thread = threading.Thread(
        target=receive_file,
        args=(received_file,)
    )
    receiver_thread.daemon = True
    receiver_thread.start()
    
    time.sleep(1)
    send_file("127.0.0.1", source_file)
    time.sleep(2)
    
    # Verify files match
    if os.path.exists(received_file):
        if filecmp.cmp(source_file, received_file):
            print("✅ Test passed: Files match!")
        else:
            print("❌ Test failed: Files don't match")
    else:
        print("❌ Test failed: Received file doesn't exist")
    
    try:
        os.remove(source_file)
        os.remove(received_file)
        os.rmdir(test_dir)
    except:
        pass

if __name__ == "__main__":
    test_file_transfer()