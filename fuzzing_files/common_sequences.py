import itertools
import concurrent.futures
from typing import List, Dict, Tuple
import time
import os

# Define comprehensive common keyboard sequences
common_sequences = {
    "sequential_characters": [
        "qwerty", "asdf", "zxcvbn", "qwertyuiop", "asdfgh", "qazwsx",
        "123456", "123456789", "qwerty123", "asdf123", "zxcvbnm",
        "qwertyui", "asdfghjkl", "qwertyuiopasdf", "12345678"
    ],
    "numeric_sequences": [
                             ''.join(num) for length in range(2, 6) for num in
                             itertools.product('0123456789', repeat=length)
                         ] + [
                             '123123', '456456', '789789'  # Adding common patterns
                         ],
    "repetitive_characters": [
        ''.join(char) for length in range(2, 6) for char in
        itertools.product('abcdefghijklmnopqrstuvwxyz', repeat=length)
    ],
    "common_words": [
        "password", "letmein", "welcome", "admin", "user", "test",
        "abc123", "iloveyou", "monkey", "dragon", "sunshine",
        "qwerty", "football", "baseball", "trustno1", "iloveyou123", "openme"
    ],
    "common_phrases": [
        "qwertyuiop", "password1", "12345", "letmein123", "trustno1",
        "sunshine", "football", "baseball", "iloveyou123", "welcome123",
        "letmein!", "1234567", "qwerty12345", "password123", "hello123"
    ],
    "keyboard_patterns": [
        # Horizontal Patterns
        "qwerty", "asdf", "zxcv", "qwertyuiop", "asdfgh", "qazwsx",
        "123456", "123456789", "qwerty123", "asdf123", "zxcvbnm",
        "qwertyui", "asdfghjkl", "qwertyuiopasdf", "12345678",

        # Vertical Patterns
        "qaz", "wsx", "edc", "rfv", "tgb", "yhn", "ujm",
        "ik,", "ol.", "p;/", "123", "456", "789", "0-=",

        # Diagonal Patterns
        "rfv", "tgb", "yhn", "ujm", "ik,", "ol.",

        # Combinations of Letters and Numbers
        "qwerty123", "asdf123", "zxcvbn123", "qwertyui", "asdfgh",
        "qwertyuiop123", "1234567890", "qwertyuiopasdfghjkl",
        "qwertyuiopasdfghjklzxcvbnm", "qwertyuiopasdfghjkl;",

        # Extended Patterns
        "qwertyuiopasdfghjklzxcvbnm1234567890",
        "qwertyuiopasdfghjklzxcvbnm!@#$%^&*()",
        "qwertyuiopasdfghjklzxcvbnm,./;'[]",
        "qwertyuiopasdfghjklzxcvbnm<>?:\"{}|",

        # Patterns with Special Characters
        "qwertyuiopasdfghjklzxcvbnm1234567890!@#$%^&*()",
        "qwertyuiopasdfghjklzxcvbnm!@#$%^&*()_+",
        "qwertyuiopasdfghjklzxcvbnm1234567890-=~",
        "qwertyuiopasdfghjklzxcvbnm!@#$%^&*()_+[]{}",
        "qwertyuiopasdfghjklzxcvbnm!@#$%^&*()_+<>?",

        # Additional Patterns
        "qwertyuiopasdfghjklzxcvbnm1234567890!@#$%^&*()_+<>?",
        "qwertyuiopasdfghjklzxcvbnm!@#$%^&*()_+[]{}",
        "qwertyuiopasdfghjklzxcvbnm1234567890-=~",
        "qwertyuiopasdfghjklzxcvbnm!@#$%^&*()_+<>?",

        # Repeated Patterns
        "qwertyqwerty", "asdfasdf", "zxcvzxcv", "123123", "456456",
        "789789", "qwertyuiopqwertyuiop", "asdfghjklasdfghjkl",

        # Numeric Patterns
        "00", "11", "22", "33", "44", "55", "66", "77", "88", "99",
        "000", "111", "222", "333", "444", "555", "666", "777", "888", "999",
        "0000", "1111", "2222", "3333", "4444", "5555", "6666", "7777", "8888", "9999",

        # Mixed Patterns
        "qwerty123456", "asdfgh123456", "zxcvbn123456", "qwerty!@#$", "asdfgh!@#$",
        "zxcvbn!@#$", "qwerty123!@#$", "asdfgh123!@#$", "zxcvbn123!@#$"
    ],
}

# Function to check if a specific sequence is common
def is_common_sequence(sequence: str, category: str) -> bool:
    """Check if a specific sequence is common in the given category."""
    return sequence in common_sequences.get(category, [])

# Function to generate concatenated patterns using chunking and parallel concurrency
def generate_concatenated_patterns(sequences: Dict[str, List[str]]) -> List[str]:
    def concatenate_chunk(chunk: Tuple[List[str], List[str], List[str]]) -> List[str]:
        common_words, keyboard_patterns, sequential_characters = chunk
        concatenated_patterns = []

        # Concatenate common words with keyboard patterns
        for word in common_words:
            for pattern in keyboard_patterns:
                concatenated_patterns.append(word + pattern)

        # Concatenate common words with sequential characters
        for word in common_words:
            for seq in sequential_characters:
                concatenated_patterns.append(word + seq)

        # Concatenate common words with numeric sequences
        for word in common_words:
            for num_seq in sequences["numeric_sequences"]:
                concatenated_patterns.append(word + num_seq)

        # Example: Concatenate name + birthdate (assuming a sample name and birthdate)
        sample_name = "john"
        sample_birthdate = "1971"
        concatenated_patterns.append(sample_name + sample_birthdate)

        # Example: Concatenate common word + year
        for word in common_words:
            for year in range(1900, 2101):  # Example years
                concatenated_patterns.append(word + str(year))

        return concatenated_patterns

    # Split the sequences into chunks
    chunk_size = 100  # Adjust chunk size as needed
    common_words_chunks = [sequences["common_words"][i:i + chunk_size] for i in range(0, len(sequences["common_words"]), chunk_size)]
    keyboard_patterns_chunks = [sequences["keyboard_patterns"][i:i + chunk_size] for i in range(0, len(sequences["keyboard_patterns"]), chunk_size)]
    sequential_characters_chunks = [sequences["sequential_characters"][i:i + chunk_size] for i in range(0, len(sequences["sequential_characters"]), chunk_size)]

    # Create a ThreadPoolExecutor
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Process each chunk concurrently
        futures = [executor.submit(concatenate_chunk, (common_words, keyboard_patterns, sequential_characters))
                   for common_words, keyboard_patterns, sequential_characters in
                   zip(common_words_chunks, keyboard_patterns_chunks, sequential_characters_chunks)]

        # Collect results
        results = [future.result() for future in concurrent.futures.as_completed(futures)]

        # Combine results
        combined_concatenated_patterns = [item for sublist in results for item in sublist]

        return combined_concatenated_patterns

# Function to add a common sequence to a password
def add_common_sequence_to_password(password: str, category: str, index: int = 0) -> str:
    """Add a common sequence to a password."""
    sequences = common_sequences.get(category, [])
    if index < 0 or index >= len(sequences):
        raise ValueError("Index out of range")
    return password + sequences[index]

# Function to convert common_sequences to a set using chunking and concurrency
def convert_to_set_with_chunking(data: Dict[str, List[str]]) -> set:
    def process_chunk(chunk: List[str]) -> set:
        return {item for sublist in chunk for item in sublist}

    # Determine the number of chunks
    num_chunks = len(data)

    # Split the data into chunks
    chunks = [list(data.values())[i::num_chunks] for i in range(num_chunks)]

    # Create a ThreadPoolExecutor
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Process each chunk concurrently
        futures = [executor.submit(process_chunk, chunk) for chunk in chunks]

        # Collect results
        results = [future.result() for future in concurrent.futures.as_completed(futures)]

        # Combine results
        combined_set = set.union(*results)

        return combined_set

# Function to write a set to a file
def write_set_to_file(file_path: str, data_set: set) -> None:
    # Check if the file exists, if not create it
    if not os.path.exists(file_path):
        with open(file_path, 'w') as file:
            pass  # Create an empty file

    with open(file_path, 'w') as file:
        for item in data_set:
            file.write(f"{item}\n")

# Function to write the entire dictionary to a text file
def write_dict_to_file(file_path: str, data_dict: Dict[str, List[str]]) -> None:
    with open(file_path, 'w') as file:
        for key, value in data_dict.items():
            file.write(f"{key}:\n")
            for item in value:
                file.write(f"  {item}\n")

# Example usage
if __name__ == "__main__":
    # Generate concatenated patterns
    start_time = time.time()
    concatenated_patterns = generate_concatenated_patterns(common_sequences)

    # Count unique concatenated patterns
    unique_concatenated_patterns = set(concatenated_patterns)
    print("Total Unique Concatenated Patterns:", len(unique_concatenated_patterns))

    # Example of checking sequences
    test_sequence = "openme1971"
    if test_sequence in unique_concatenated_patterns:
        print(f"{test_sequence} is a common keyboard pattern.")
    if is_common_sequence(test_sequence, "keyboard_patterns"):
        print(f"{test_sequence} is a common keyboard pattern.")
    else:
        print(f"{test_sequence} is not a common keyboard pattern.")

    # Convert common_sequences to a set using chunking and concurrency
    common_sequences_set = convert_to_set_with_chunking(common_sequences)
    print(f"{common_sequences_set} length common_sequences:{len(common_sequences_set)}")

    # Write results to separate text files
    write_set_to_file('unique_concatenated_patterns.txt', unique_concatenated_patterns)
    write_set_to_file('common_sequences_set.txt', common_sequences_set)

    # Write the entire common_sequences dictionary to a text file
    write_dict_to_file('common_sequences_dict.txt', common_sequences)

    elapsed_time = time.time() - start_time
    print(f"Time elapsed: {elapsed_time}")
