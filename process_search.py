import multiprocessing
from multiprocessing import current_process, Queue
from pathlib import Path
import logging
import time

logger = logging.getLogger()
stream_handler = logging.StreamHandler()
logger.addHandler(stream_handler)
logger.setLevel(logging.DEBUG)

# Function to search for keywords in files
def search_files(files, keywords, result_queue):
    logger.debug(f'Started {current_process().name}')
    results = {}
    for file in files:
        with file.open() as f:
            content = f.read()
            for keyword in keywords:
                if keyword in content:
                    if keyword not in results:
                        results[keyword] = []
                    results[keyword].append(file)
    result_queue.put(results)

# Function to divide files among processes
def divide_files(files, num_processes):
    file_groups = []
    for i in range(num_processes):
        file_groups.append(files[i::num_processes])
    return file_groups

# Function to perform keyword search in parallel
def parallel_search(files, keywords, num_processes):
    logger.debug(f'Started {current_process().name}')
    file_groups = divide_files(files, num_processes)
    start_time = time.time()  # Record start time
    result_queue = Queue()
    processes = []
    
    # Create and start processes
    for files in file_groups:
        process = multiprocessing.Process(target=search_files, args=(files, keywords, result_queue))
        process.start()
        processes.append(process)
    
    # Wait for all processes to complete
    for process in processes:
        process.join()
    
    # Gather results from the queue
    final_results = {}
    while not result_queue.empty():
        result = result_queue.get()
        for keyword, files in result.items():
            if keyword not in final_results:
                final_results[keyword] = []
            final_results[keyword].extend(files)
    
    end_time = time.time()  # Record end time
    logger.debug(f'Finished {current_process().name} in {end_time - start_time} seconds')
    
    return final_results

if __name__ == "__main__":
    # List of files to search
    files = [Path("file1.txt"), Path("file2.txt"), Path("file3.txt"), Path("file4.txt"), Path("file5.txt")]
    
    # Keywords to search for
    keywords = ["keyword1", "keyword2", "keyword3"]
    
    # Number of processes to use
    num_processes = 3
    
    # Perform parallel search
    results = parallel_search(files, keywords, num_processes)
    
    # Output search results
    print(results)
