### Useful repo to fuzz
https://github.com/danielmiessler/SecLists

Generated fuzzing files: 
https://drive.google.com/drive/folders/113N3NA7_dqMjWOPSFm-GMS5hwuucB3T2?usp=sharing

Places to look for common names: 

1. **United States**
   - [U.S. Census Bureau](https://www.census.gov/)
  - https://www.ssa.gov/oact/babynames/
    
2. **Canada**
   - [Statistics Canada](https://www.statcan.gc.ca/)

3. **United Kingdom**
   - [Office for National Statistics (ONS)](https://www.ons.gov.uk/)

4. **Australia**
   - [Australian Bureau of Statistics (ABS)](https://www.abs.gov.au/)

5. **Germany**
   - [Statistisches Bundesamt (Destatis)](https://www.destatis.de/)

6. **France**
   - [Institut national de la statistique et des études économiques (INSEE)](https://www.insee.fr/)

7. **Japan**
   - [Statistics Bureau of Japan](https://www.stat.go.jp/english/)

8. **India**
   - [Office of the Registrar General and Census Commissioner](https://censusindia.gov.in/)

9. **China**
   - [National Bureau of Statistics of China](http://www.stats.gov.cn/english/)

10. **Brazil**
    - [Instituto Brasileiro de Geografia e Estatística (IBGE)](https://www.ibge.gov.br/)

11. **Russia**
    - [Federal State Statistics Service (Rosstat)](https://www.gks.ru/eng/)

12. **South Africa**
    - [Statistics South Africa](https://www.statssa.gov.za/)

13. **Mexico**
    - [Instituto Nacional de Estadística y Geografía (INEGI)](https://www.inegi.org.mx/)

14. **Italy**
    - [Istituto Nazionale di Statistica (ISTAT)](https://www.istat.it/)

15. **South Korea**
    - [Statistics Korea](https://kostat.go.kr/portal/eng/)

16. **Spain**
    - [Instituto Nacional de Estadística (INE)](https://www.ine.es/)

17. **Netherlands**
    - [Centraal Bureau voor de Statistiek (CBS)](https://www.cbs.nl/en-gb)

18. **Sweden**
    - [Statistics Sweden](https://www.scb.se/en/)

19. **Switzerland**
    - [Federal Statistical Office](https://www.bfs.admin.ch/bfs/en/home.html)

20. **Argentina**
    - [Instituto Nacional de Estadística y Censos (INDEC)](https://www.indec.gob.ar/)
   
To alter the dictionary and generate new concatenated patterns with the provided script, you can modify the `common_sequences` dictionary by adding new categories or extending existing ones. Here are some steps and examples to guide you through the process:

### Steps to Alter the Dictionary

1. **Add New Categories**: Introduce new categories of sequences that you want to include in the concatenated patterns.
2. **Extend Existing Categories**: Add more sequences to the existing categories to increase the variety of patterns.
3. **Modify the `generate_concatenated_patterns` Function**: Ensure that the function can handle the new categories and sequences.

### Example Modifications

#### 1. Adding a New Category

Let's add a new category called `special_characters` that includes common special character sequences.

```python
common_sequences = {
    # Existing categories...
    "special_characters": [
        "!@#$%", "^&*()", "[]{}", "<>?", "~`", "|\\",
        "!@#$%^&*()", "[]{}<>?", "~`|\\", "!@#$%^&*()[]{}<>?",
        "!@#$%^&*()[]{}<>?~`|\\"
    ],
    # Other existing categories...
}
```

#### 2. Extending Existing Categories

Let's extend the `common_words` category with additional words.

```python
common_sequences = {
    # Existing categories...
    "common_words": [
        "password", "letmein", "welcome", "admin", "user", "test",
        "abc123", "iloveyou", "monkey", "dragon", "sunshine",
        "qwerty", "football", "baseball", "trustno1", "iloveyou123",
        "openme", "hello", "world", "example", "sample"
    ],
    # Other existing categories...
}
```

#### 3. Modifying the `generate_concatenated_patterns` Function

Ensure that the function can handle the new categories and sequences. You may need to update the function to include the new category in the concatenation process.

```python
def generate_concatenated_patterns(sequences: Dict[str, List[str]]) -> List[str]:
    def concatenate_chunk(chunk: Tuple[List[str], List[str], List[str], List[str]]) -> List[str]:
        common_words, keyboard_patterns, sequential_characters, special_characters = chunk
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

        # Concatenate common words with special characters
        for word in common_words:
            for spec_char in special_characters:
                concatenated_patterns.append(word + spec_char)

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
    special_characters_chunks = [sequences["special_characters"][i:i + chunk_size] for i in range(0, len(sequences["special_characters"]), chunk_size)]

    # Create a ThreadPoolExecutor
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Process each chunk concurrently
        futures = [executor.submit(concatenate_chunk, (common_words, keyboard_patterns, sequential_characters, special_characters))
                   for common_words, keyboard_patterns, sequential_characters, special_characters in
                   zip(common_words_chunks, keyboard_patterns_chunks, sequential_characters_chunks, special_characters_chunks)]

        # Collect results
        results = [future.result() for future in concurrent.futures.as_completed(futures)]

        # Combine results
        combined_concatenated_patterns = [item for sublist in results for item in sublist]

        return combined_concatenated_patterns
```

### Running the Script

After making the modifications, you can run the script to generate the new concatenated patterns. The script will process the updated dictionary and produce the desired patterns.

```python
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
```

By following these steps, you can alter the dictionary to include new categories and sequences, and generate new concatenated patterns using the script.

This Python script is designed to generate and analyze common keyboard sequences, including sequential characters, numeric sequences, repetitive characters, common words, common phrases, and various keyboard patterns. The script utilizes concurrent processing to efficiently handle large datasets and provides functionalities to check if a sequence is common, generate concatenated patterns, and write results to files.
Features

    Comprehensive Keyboard Sequences: Defines a wide range of common keyboard sequences categorized into different types.
    Concurrency: Utilizes concurrent.futures.ThreadPoolExecutor for parallel processing to improve performance.
    Sequence Checking: Provides a function to check if a specific sequence is common within a given category.
    Pattern Generation: Generates concatenated patterns using chunking and parallel concurrency.
    File Operations: Writes sets and dictionaries to text files for persistent storage.

Requirements

    Python 3.x
    itertools
    concurrent.futures
    typing
    time
    os

Usage
Functions

    is_common_sequence(sequence: str, category: str) -> bool
        Checks if a specific sequence is common in the given category.

    generate_concatenated_patterns(sequences: Dict[str, List[str]]) -> List[str]
        Generates concatenated patterns using chunking and parallel concurrency.

    add_common_sequence_to_password(password: str, category: str, index: int = 0) -> str
        Adds a common sequence to a password.

    convert_to_set_with_chunking(data: Dict[str, List[str]]) -> set
        Converts common sequences to a set using chunking and concurrency.

    write_set_to_file(file_path: str, data_set: set) -> None
        Writes a set to a file.

    write_dict_to_file(file_path: str, data_dict: Dict[str, List[str]]) -> None
        Writes the entire dictionary to a text file.

Example Usage

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

Output Files

    unique_concatenated_patterns.txt: Contains unique concatenated patterns.
    common_sequences_set.txt: Contains the set of common sequences.
    common_sequences_dict.txt: Contains the entire common sequences dictionary.
