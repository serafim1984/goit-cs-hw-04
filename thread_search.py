import threading
from pathlib import Path
import logging
import time

# Function to search for keywords in files
def search_files(files, keywords):
    results = {}
    for file in files:
        try:
            with file.open() as f:
                content = f.read()
                for keyword in keywords:
                    if keyword in content:
                        if keyword not in results:
                            results[keyword] = []
                        results[keyword].append(file)
        except Exception as e:
            logging.error(f"Error reading file '{file}': {e}")
    return results

# Function to divide files among threads
def divide_files(files, num_threads):
    file_groups = []
    for i in range(num_threads):
        file_groups.append(files[i::num_threads])
    return file_groups

# Function to perform keyword search in parallel
def parallel_search(files, keywords, num_threads):
    file_groups = divide_files(files, num_threads)
    threads = []
    results = {}
    
    # Define worker function for each thread
    def worker(files):
        logging.debug('Start')
        thread_results = search_files(files, keywords)
        with lock:
            for keyword, files in thread_results.items():
                if keyword not in results:
                    results[keyword] = []
                results[keyword].extend(files)
    
    # Create and start threads
    start_time = time.time()
    for files in file_groups:
        thread = threading.Thread(target=worker, args=(files,))
        thread.start()
        threads.append(thread)
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    end_time = time.time()
    logging.debug(f'Execution time: {end_time - start_time} seconds')
    
    return results

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG, format='%(threadName)s %(message)s')

    # List of files to search
    files = [Path("file1.txt"), Path("file2.txt"), Path("file3.txt"), Path("file4.txt"), Path("file5.txt")]
    
    # Keywords to search for
    keywords = ["keyword1", "keyword2", "keyword3"]
    
    # Number of threads to use
    num_threads = 3
    
    # Create a lock for thread safety
    lock = threading.Lock()
    
    try:
        # Perform parallel search
        results = parallel_search(files, keywords, num_threads)
        
        # Output search results as a dictionary
        print(results)
    
    except Exception as e:
        logging.error(f"An error occurred: {e}")

    logging.debug('End program')

