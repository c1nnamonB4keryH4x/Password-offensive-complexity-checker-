import threading
import os
import time
from typing import List, Optional


class CacheManager:
    def __init__(self):
        self.cache = []  # List to hold cached strings

    def add_to_cache(self, items: List[str]):
        """Add items to the cache."""
        self.cache.extend(items)

    def read_files_to_cache(self, file_paths: list[str]):
        """Read contents of files and add them to the cache."""
        for file_path in file_paths:
            if os.path.isfile(file_path):
                try:
                    with open(file_path, 'rb') as f:  # Open in binary mode
                        content = f.read()
                        # Decode the content using a fallback encoding
                        try:
                            decoded_content = content.decode('utf-8')
                        except UnicodeDecodeError:
                            decoded_content = content.decode('ISO-8859-1', errors='ignore')  # Fallback
                        # Split content into lines and add to cache
                        lines = decoded_content.splitlines()
                        self.add_to_cache(lines)
                except Exception as e:
                    print(f"Error reading file {file_path}: {e}")
            else:
                print(f"File not found: {file_path}")
    def search_in_cache(self, indices: List[int], search_string: str) -> List[int]:
        """Search for a string in the cache at specified indices."""
        found_indices = []
        for index in indices:
            if index < len(self.cache) and self.cache[index] == search_string:
                found_indices.append(index)
        return found_indices

    def chunk_indices(self, indices: List[int], chunk_size: int) -> List[List[int]]:
        """Divide the list of indices into chunks."""
        return [indices[i:i + chunk_size] for i in range(0, len(indices), chunk_size)]

    def search_chunk(self, indices: List[int], search_string: str, results: List[int], lock: threading.Lock):
        """Search for a string in a chunk of the cache."""
        found_indices = self.search_in_cache(indices, search_string)
        with lock:  # Ensure thread-safe access to results
            results.extend(found_indices)

    def run_search_in_threads(self, search_string: str, num_threads: int) -> List[int]:
        """Run search in threads for the specified search string."""
        indices = list(range(len(self.cache)))  # Create a list of indices
        chunks = self.chunk_indices(indices, len(indices) // num_threads + 1)  # Chunk the indices

        threads = []
        results = []  # List to hold results
        lock = threading.Lock()  # Lock for thread-safe access to results

        # Create and start threads
        for chunk in chunks:
            thread = threading.Thread(target=self.search_chunk, args=(chunk, search_string, results, lock))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        return results

    def flush_cache(self):
        """Flush the cache."""
        self.cache.clear()  # Clear the cache
        print("Cache flushed.")


def main():
    # Create an instance of CacheManager
    manager = CacheManager()

    # Prompt the user to enter file paths
    file_paths_input = input("Enter the file paths separated by commas: ")
    file_paths = [path.strip() for path in file_paths_input.split(',')]

    # Load multiple files into the cache
    manager.read_files_to_cache(file_paths)

    # Define the search string and number of threads
    search_string = input("Enter the string to search for in the cache: ")

    fastest_time = float('inf')
    fast_thread_num = 0

    # Specify the output file for results
    output_file = input("Enter the output file path to save results: ")

    # Ensure the output file exists or create it
    try:
        if not os.path.exists(output_file):
            with open(output_file, 'a') as f:
                pass  # Create an empty file
            print(f"Created output file: {output_file}")

    except Exception as e:
        print(f"Error creating output file {output_file}: {e}")
        return  # Exit if we can't create the output file

    # Open the output file for writing
    try:
        with open(output_file, 'a') as result_file:
            result_file.write(f"Files read into cache: {file_paths_input}\n")

            for i in range(1, 15):
                num_threads = i
                print(f"Num threads: {i} ")

                # Start timestamp
                start_time = time.time()

                # Run the search in threads
                found_indices = manager.run_search_in_threads(search_string, num_threads)

                # End timestamp
                end_time = time.time()

                # Calculate time taken
                time_taken = end_time - start_time

                # Write the results to the output file
                result_file.write(f"Found '{search_string}' at indices: {found_indices}\n")
                result_file.write(f"Total indices searched: {len(manager.cache)}\n")
                result_file.write(f"Time taken for search: {time_taken:.4f} seconds\n")

                # Check for the fastest time
                if time_taken < fastest_time:
                    fastest_time = time_taken
                    fast_thread_num = i

            # Write the fastest time to the output file
            result_file.write(f"Fastest time: {fastest_time:.4f} seconds with {fast_thread_num} threads\n")

    except Exception as e:
        print(f"Error writing to output file {output_file}: {e}")

    # Flush the cache
    manager.flush_cache()

if __name__ == "__main__":
    main()