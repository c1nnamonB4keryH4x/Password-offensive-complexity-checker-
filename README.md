# Password Complexity Checker

## Overview

The **Password Complexity Checker** is a comprehensive tool designed to evaluate the strength of passwords based on various criteria, including complexity, entropy, and compliance with known vulnerabilities. The tool provides a user-friendly interface for inputting passwords and configuring settings for the evaluation process.

## Table of Contents

1. [Features](#features)
2. [Installation](#installation)
3. [Usage](#usage)
   - [Input Fields](#input-fields)
   - [Password Checking](#password-checking)
   - [Viewing Results](#viewing-results)
   - [Advanced Features](#advanced-features)
4. [Code Structure](#code-structure)
   - [Main Files](#main-files)
   - [Fuzzing Files](#fuzzing-files)
   - [Lexo Patterns](#lexo-patterns)
   - [Menu Implementation](#menu-implementation)
5. [Implementation Details](#implementation-details)
   - [Password Evaluation Logic](#password-evaluation-logic)
   - [Sharding and Multi-threading](#sharding-and-multi-threading)
   - [Leet Speak Conversion](#leet-speak-conversion)
6. [Troubleshooting](#troubleshooting)
7. [FAQs](#faqs)
8. [Contributing](#contributing)
9. [License](#license)

## Features

- **Password Evaluation**: Check passwords against known vulnerabilities and calculate complexity scores.
- **Known Passwords Loading**: Load known passwords from specified files for comparison.
- **Strong Password Generation**: Generate strong passwords that meet complexity requirements.
- **Multi-threaded Processing**: Efficiently handle large datasets using multi-threading.
- **Customizable Wordlists**: Specify your own wordlists for evaluation.

## Installation

To install the Password Complexity Checker, clone the repository and install the required dependencies:

```bash
git clone https://github.com/c1nnamonB4keryH4x/Password-offensive-complexity-checker-.git
cd Password-offensive-complexity-checker-
```

Make sure you have Python 3.x installed. You can install the required packages using:

```bash
pip install -r requirements.txt
```
Under the depencies folder there is a bat file for Windows and sh file for linux to help install dependencies. 
## Usage

### Input Fields

Upon launching the tool, you will be greeted with a user-friendly interface that allows you to input passwords and configure settings for the evaluation process.

- **Variant Path**: Enter the path to the variant file or click "Browse" to select it.
- **Common Passwords Path**: Enter the path to the common passwords file or click "Browse" to select it.
- **Wordlist Path**: Enter the path to the wordlist file or click "Browse" to select it.
- **Password Entry**: Input the password you wish to evaluate in the designated field.

### Password Checking

- **Check Password**: Click the "Check Password" button to initiate the evaluation process.
- **Options**: You can choose to check variants by checking the "Check Variants" checkbox.

### Viewing Results

The results of the password evaluation will be displayed in a scrollable text box at the bottom of the interface. Results include:

- Loaded known passwords count
- Time taken for evaluation
- Exact and partial match findings
- Password complexity scores (entropy, compliance, crackability)
- Suggestions for strong passwords

### Advanced Features

#### Loading Known Passwords

The tool allows you to load known passwords from specified files. You can input multiple file paths separated by commas. The tool will attempt to load passwords from the provided paths and display the count of loaded passwords.

#### Generating Strong Passwords

The tool can generate strong passwords that meet complexity requirements. You can specify the desired length for the generated password. Generated passwords will be displayed in the results section.

## Code Structure

### Main Files

- **README.md**: This documentation file.
- **Uniqueness_scoring_Chunk_sharding_dynamic_multi_threading.py**: Contains the main logic for evaluating password uniqueness and complexity using sharding and multi-threading.
- **final_menu.py**:final code implementations.
- **lexoPatterns.py**: Separate file that gives the raw lexographical pattern implementation generators, can be used to help generate unique wordlists

### Fuzzing Files

- **fuzzing_files/Fuzzing_guide.md**: A guide on useful resources for fuzzing and generating fuzzing files.
- **fuzzing_files/common_sequences.py**: Contains common keyboard sequences and functions to generate concatenated patterns using chunking and concurrency.

### Lexo Patterns

The **lexoPatterns.py** file contains the `AdvancedLeetSpeakConverter` class, which provides functionalities for converting text into leet speak using various strategies. The key features include:

- **Capitalization**: Methods to capitalize the first letter, last letter, or both.
- **Repetition**: A method to repeat a word a specified number of times.
- **Leet Speak Conversion**: Multiple strategies for converting characters to their leet speak equivalents, including random, first, last, and comprehensive replacements.
- **Multi-Variant Generation**: Generate multiple variants of a given text using different strategies.
- **Replacement Patterns**: Generate patterns for replacing characters in a text.

### Menu Implementation

The menu implementation is designed to provide a user-friendly interface for interacting with the tool. It includes options for:

- Loading known passwords from files or sets.
- Performing searches for exact or partial matches.
- Generating strong passwords.
- Clearing the known passwords list.

The main function orchestrates the flow of the program, allowing users to input their preferences and view results interactively.

## Implementation Details

### Password Evaluation Logic

The password evaluation logic is implemented in the `Uniqueness_scoring_Chunk_sharding_dynamic_multi_threading.py` file. The key components include:

- **ShardingStorageTransformer**: A class that implements sharding as a storage transformer, allowing for efficient storage and retrieval of password data.
- **_ShardIndex**: A helper class that manages the indexing of chunks within the sharded storage.
- **Password Searching**: Functions to search for exact and partial matches of passwords within the loaded known passwords.

### Sharding and Multi-threading

The tool utilizes sharding to divide the password data into manageable chunks, allowing for efficient processing. Multi-threading is employed to perform searches concurrently, improving performance when handling large datasets. The `worker` function is responsible for executing searches in a thread-safe manner.

### Leet Speak Conversion

The `lexoPatterns.py` file contains the logic for converting text into leet speak. The `AdvancedLeetSpeakConverter` class provides various strategies for character replacement, allowing users to generate leet speak variants of their passwords. This feature can be useful for testing the strength of passwords against common leet speak variations.

Certainly! Below is a more detailed explanation of the chunk sharding and password evaluation metrics used within the Password Complexity Checker code.

---

## Chunk Sharding

### Overview

Chunk sharding is a technique used to divide large datasets into smaller, more manageable pieces (or "chunks") that can be processed independently. This approach enhances performance and scalability, especially when dealing with large collections of passwords. In the context of the Password Complexity Checker, chunk sharding allows for efficient storage, retrieval, and searching of known passwords.

### Implementation Details

#### ShardingStorageTransformer Class

The `ShardingStorageTransformer` class is responsible for managing the sharded storage of passwords. Key components of this class include:

- **Initialization**: The constructor takes a type and a tuple representing the number of chunks per shard. It calculates the total number of chunks and initializes an inner store to hold the password data.

```python
def __init__(self, _type: str, chunks_per_shard: Tuple[int, ...]) -> None:
    if isinstance(chunks_per_shard, int):
        chunks_per_shard = (chunks_per_shard,)
    self.chunks_per_shard = chunks_per_shard
    self._num_chunks_per_shard = int(math.prod(chunks_per_shard))
    self.inner_store = {}
    self.known_passwords = []  # Initialize known_passwords
```

- **Key to Shard Mapping**: The `_key_to_shard` method maps a given chunk key to its corresponding shard key. This mapping is essential for determining where to store or retrieve a specific chunk of data.

```python
def _key_to_shard(self, chunk_key: str) -> Tuple[str, Tuple[int, ...]]:
    prefix, _, chunk_string = chunk_key.rpartition("c")
    chunk_subkeys = tuple(map(int, chunk_string.split("/"))) if chunk_string else (0,)
    shard_key_tuple = tuple(subkey // shard_i for subkey, shard_i in zip(chunk_subkeys, self.chunks_per_shard))
    shard_key = prefix + "c" + "/".join(map(str, shard_key_tuple))
    return shard_key, shard_key_tuple
```

- **Reading and Writing Chunks**: The `read_chunk` and `write_chunk` methods handle the retrieval and storage of password chunks. They utilize the shard index to determine the appropriate slice of data to read or write.

```python
def read_chunk(self, key: str) -> Optional[bytes]:
    # Logic to read a chunk from the inner store
    ...

def write_chunk(self, key: str, value: bytes) -> None:
    # Logic to write a chunk to the inner store
    ...
```

#### _ShardIndex Class

The `_ShardIndex` class manages the indexing of chunks within the sharded storage. It keeps track of offsets and lengths for each chunk, allowing for efficient access to the data.

- **Localizing Chunks**: The `__localize_chunk__` method converts a chunk's index to its corresponding index within the shard.

```python
def __localize_chunk__(self, chunk: Tuple[int, ...]) -> Tuple[int, ...]:
    return tuple(chunk_i % shard_i for chunk_i, shard_i in zip(chunk, self.store.chunks_per_shard))
```

- **Chunk Slicing**: The `get_chunk_slice` method retrieves the slice of data corresponding to a specific chunk, while the `set_chunk_slice` method updates the index with the new slice information.

```python
def get_chunk_slice(self, chunk: Tuple[int, ...]) -> Optional[slice]:
    # Logic to get the chunk slice
    ...

def set_chunk_slice(self, chunk: Tuple[int, ...], chunk_slice: Optional[slice]) -> None:
    # Logic to set the chunk slice
    ...
```

### Benefits of Chunk Sharding

- **Scalability**: By dividing the password data into chunks, the system can handle larger datasets without performance degradation.
- **Parallel Processing**: Multiple threads can work on different chunks simultaneously, improving the overall speed of password evaluation.
- **Efficient Memory Usage**: Only the necessary chunks are loaded into memory, reducing the memory footprint of the application.

---

## Password Evaluation Metrics

The Password Complexity Checker evaluates passwords based on several metrics that assess their strength and compliance with security standards. The key metrics include:

### 1. Entropy

Entropy is a measure of randomness and unpredictability in a password. It quantifies the amount of uncertainty associated with a password and is calculated using the formula:
$$
\text{Entropy} = -\sum_{i} p_i \cdot \log_2(p_i)
$$


In this formula:

    p_i represents the probability of each unique character in the password.

    The logarithm is base 2, denoted as log⁡_2​.

#### Implementation

The `calculate_entropy` method in the `BaseComplexity` class computes the entropy of a given password:

```python
def calculate_entropy(self, password: str) -> float:
    length = len(password)
    unique_chars = len(set(password))
    if unique_chars == 0:
        return 0
    char_count = Counter(password)
    probabilities = [count / length for count in char_count.values()]
    entropy = -sum(p * math.log2(p) for p in probabilities)
    return entropy
```

### 2. Compliance Score

The compliance score checks whether a password meets specific security standards, such as those set by OWASP and NIST. These standards typically require a mix of character types (lowercase, uppercase, digits, and special characters) and a minimum length.

#### Implementation

The `calculate_compliance_score` method evaluates a password against a predefined regex pattern:

```python
def calculate_compliance_score(self, password: str) -> float:
    regex = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+[\]{};":\\|,.<>?]).{8,}$'
    if re.match(regex, password):
        return 10  # Fully compliant
    return 0  # Not compliant
```

### 3. Crackability Score

The crackability score assesses how easily a password can be guessed or cracked based on its composition and known vulnerabilities. This score takes into account the number of times a password has been found in known password databases.

#### Implementation

The `calculate_crackability_score` method calculates the score based on the number of hits a password has received:

```python
def calculate_crackability_score(self, password: str, password_hits: int, common_hit: Optional[int] = None) -> float:
    # Logic to calculate the crackability score
    ...
```

### 4. Overall Complexity Score

The overall complexity score combines the entropy, compliance, and crackability scores into a single metric that reflects the strength of a password. Weights are assigned to each component to reflect their importance in the overall evaluation.

#### Implementation

The `calculate_overall_complexity` method in the `ActualSecurity` class computes the overall complexity score:

```python
def calculate_overall_complexity(self, password: str, password_hits: int, com_hit: int) -> float:
    # Calculate base complexity scores
    base_complexity = BaseComplexity(password)
    entropy_score = base_complexity.calculate_entropy(password)
    standardized_entropy = base_complexity.standardize_entropy(entropy_score)
    compliance_score = base_complexity.calculate_compliance_score(password)

    # Calculate crackability score
    crackability_score = self.calculate_crackability_score(password, password_hits, com_hit)

    # Weights for the composite score
    w_e = 0.35  # Weight for entropy score
    w_c = 0.15  # Weight for compliance score
    w_k = 0.35  # Weight for crackability score
    w_m = 0.15  # Weight for MD5 resistance score

    # Combined score
    overall_complexity_score = self.calculate_weighted_average(
        [w_e * standardized_entropy,
         w_c * compliance_score,
         w_k * max(-10, crackability_score),
         w_m * md5_resistance]
    )

    return max(0, overall_complexity_score)
```

## Troubleshooting

### Common Issues

- **File Not Found**: Ensure that the paths entered for variant, common passwords, and wordlist files are correct.
- **Encoding Errors**: The tool attempts to load files using multiple encodings. If you encounter issues, check the file encoding.
- **Performance Issues**: If the tool is slow, consider optimizing the wordlist or reducing the number of passwords being checked.
- **Imports not working**: Make sure all depencies have been installed and none of them have been moved resulting in errors.

## FAQs

**Q1: What types of passwords can I check?**  
A1: You can check any password, including common passwords, complex passwords, and passphrases.

**Q2: How does the tool calculate password strength?**  
A2: The tool calculates password strength using metrics such as entropy, compliance with standards, and crackability scores based on known vulnerabilities.

**Q3: Can I customize the wordlists used for evaluation?**  
A3: Yes, you can specify your own wordlists by providing the file paths in the input fields.

## Contributing

Contributions are welcome! If you have suggestions for improvements or new features, please open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE.txt) file for details.

This README provides a comprehensive overview of the Password Complexity Checker, including its features, installation instructions, usage guidelines, code structure, implementation details, troubleshooting tips, FAQs, and contribution guidelines. Feel free to modify any sections as needed!

