import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog, scrolledtext
import threading
import time
from typing import NamedTuple, Tuple, Optional, Union, List, Iterator, Set
from functools import reduce
from operator import mul
import math
import re
from collections import Counter
from typing import List
import random
import string
import hashlib
import json
import urllib.parse
import random
import hashlib
from typing import Dict, List, Set
from concurrent.futures import ThreadPoolExecutor

##Global Constants
MAX_UINT_64 = 2 ** 64 - 1
# a comma must be at the begenning because it is loaded at the end of the initial search
# change these paths to the textfiles you downloaded
COMMON_PASSWORD_PATH = "C:/Enter_path_here"
COMMON_PATTERNS_PATH = "C:/Enter_path_here"


# -------------------------------
# Chunk Sharding Section
class _ShardIndex(NamedTuple):
    store: "ShardingStorageTransformer"
    offsets_and_lengths: List[Tuple[int, int]]

    def __localize_chunk__(self, chunk: Tuple[int, ...]) -> Tuple[int, ...]:
        return tuple(chunk_i % shard_i for chunk_i, shard_i in zip(chunk, self.store.chunks_per_shard))

    def is_all_empty(self) -> bool:
        return all(offset == MAX_UINT_64 and length == MAX_UINT_64 for offset, length in self.offsets_and_lengths)

    def get_chunk_slice(self, chunk: Tuple[int, ...]) -> Optional[slice]:
        localized_chunk = self.__localize_chunk__(chunk)
        chunk_start, chunk_len = self.offsets_and_lengths[localized_chunk]
        if (chunk_start, chunk_len) == (MAX_UINT_64, MAX_UINT_64):
            return None
        else:
            return slice(int(chunk_start), int(chunk_start + chunk_len))

    def set_chunk_slice(self, chunk: Tuple[int, ...], chunk_slice: Optional[slice]) -> None:
        localized_chunk = self.__localize_chunk__(chunk)
        if chunk_slice is None:
            self.offsets_and_lengths[localized_chunk] = (MAX_UINT_64, MAX_UINT_64)
        else:
            self.offsets_and_lengths[localized_chunk] = (chunk_slice.start, chunk_slice.stop - chunk_slice.start)

    def to_bytes(self) -> bytes:
        return b''.join((offset.to_bytes(8, byteorder='little') + length.to_bytes(8, byteorder='little'))
                        for offset, length in self.offsets_and_lengths)

    @classmethod
    def from_bytes(cls, buffer: Union[bytes, bytearray], store: "ShardingStorageTransformer") -> "_ShardIndex":
        offsets_and_lengths = []
        for i in range(0, len(buffer), 16):
            offset = int.from_bytes(buffer[i:i + 8], byteorder='little')
            length = int.from_bytes(buffer[i + 8:i + 16], byteorder='little')
            offsets_and_lengths.append((offset, length))
        return cls(store=store, offsets_and_lengths=offsets_and_lengths)

    @classmethod
    def create_empty(cls, store: "ShardingStorageTransformer"):
        return cls(store=store, offsets_and_lengths=[(MAX_UINT_64, MAX_UINT_64)] * store.num_chunks_per_shard)


class ShardingStorageTransformer:
    """Implements sharding as a storage transformer."""
    extension_uri = "https://purl.org/zarr/spec/storage_transformers/sharding/1.0"
    valid_types = ["indexed"]

    def __init__(self, _type: str, chunks_per_shard: Tuple[int, ...]) -> None:
        if isinstance(chunks_per_shard, int):
            chunks_per_shard = (chunks_per_shard,)
        self.chunks_per_shard = chunks_per_shard

        try:
            self._num_chunks_per_shard = int(math.prod(chunks_per_shard))
        except AttributeError:
            self._num_chunks_per_shard = int(reduce(mul, chunks_per_shard, 1))
        self.inner_store = {}
        self.known_passwords = []  # Initialize known_passwords

    def _key_to_shard(self, chunk_key: str) -> Tuple[str, Tuple[int, ...]]:
        prefix, _, chunk_string = chunk_key.rpartition("c")
        chunk_subkeys = tuple(map(int, chunk_string.split("/"))) if chunk_string else (0,)
        shard_key_tuple = tuple(subkey // shard_i for subkey, shard_i in zip(chunk_subkeys, self.chunks_per_shard))
        shard_key = prefix + "c" + "/".join(map(str, shard_key_tuple))
        return shard_key, shard_key_tuple

    def read_chunk(self, key: str) -> Optional[bytes]:
        if key.startswith("data/"):
            shard_key, chunk_subkey = self._key_to_shard(key)
            try:
                full_shard_value = self.inner_store[shard_key]
                index = _ShardIndex.from_bytes(full_shard_value[-16 * self._num_chunks_per_shard:], self)
                chunk_slice = index.get_chunk_slice(chunk_subkey)
                if chunk_slice is not None:
                    return full_shard_value[chunk_slice]
                else:
                    raise KeyError(f"Chunk subkey '{chunk_subkey}' not found in shard '{shard_key}'.")
            except KeyError:
                raise KeyError(f"Shard key '{shard_key}' not found.")
        else:
            return self.inner_store.get(key)

    def write_chunk(self, key: str, value: bytes) -> None:
        if key.startswith("data/"):
            shard_key, chunk_subkey = self._key_to_shard(key)
            new_content = {chunk_subkey: value}
            try:
                full_shard_value = self.inner_store.get(shard_key, bytearray())
                index = _ShardIndex.from_bytes(full_shard_value[-16 * self._num_chunks_per_shard:], self)
            except KeyError:
                index = _ShardIndex.create_empty(self)
            index.set_chunk_slice(chunk_subkey, slice(len(full_shard_value), len(full_shard_value) + len(value)))
            full_shard_value += value
            full_shard_value += index.to_bytes()
            self.inner_store[shard_key] = full_shard_value
        else:
            self.inner_store[key] = value

    def load_known_passwords(self, file_paths: List[str] = None, password_set: Set[str] = None):
        """Load known passwords from multiple files or a set into the known_passwords list."""
        self.known_passwords = []
        encodings_to_try = ['utf-8', 'latin-1', 'utf-16']  # List of encodings to try

        if file_paths:
            for file_path in file_paths:
                for encoding in encodings_to_try:
                    try:
                        with open(file_path, 'r', encoding=encoding) as file:
                            self.known_passwords.extend([line.strip() for line in file if line.strip()])
                        print(f"Successfully loaded passwords from {file_path} using encoding: {encoding}")
                        break  # Exit the encoding loop if successful
                    except (UnicodeDecodeError, FileNotFoundError) as e:
                        print(f"Error loading known passwords from {file_path} with encoding {encoding}: {e}")
                else:
                    print(f"Failed to load known passwords from {file_path} with all attempted encodings.")

        if password_set:
            self.known_passwords.extend(password_set)
            print(f"Successfully loaded passwords from set with {len(password_set)} items.")

    def clear_known_passwords(self):
        """Clear the known_passwords list."""
        self.known_passwords.clear()
        print("Known passwords list has been cleared.")

    def get_known_passwords_count(self) -> int:
        """Return the number of known passwords."""
        return len(self.known_passwords)

    def search_partial_passwords(self, search_string: str) -> List[str]:
        """Search for known passwords that contain the search string."""
        found_passwords = [password for password in self.known_passwords if search_string in password]
        return found_passwords

    def search_exact_password(self, search_string: str) -> Union[str, bool]:
        """Search for an exact match of the known password from the original list."""
        normalized_search_string = search_string.strip().lower()  # Normalize the search string
        search_length = len(normalized_search_string)  # Get the length of the search string
        for password in self.known_passwords:
            normalized_password = password.strip().lower()  # Normalize passwords
            if normalized_password == normalized_search_string and len(normalized_password) == search_length:
                return password  # Return the exact match found
        return False  # Return False if no exact match is found

    def chunk_shard_search(self, search_string: str) -> Union[str, bool]:
        """Perform a chunk-sharded search and return the exact match if found."""
        found_passwords = self.search_partial_passwords(search_string)
        exact_match = self.search_exact_password(search_string)
        if exact_match:
            return exact_match
        return False


def worker(manager: ShardingStorageTransformer, search_string: str, results: List[str], lock: threading.Lock):
    """Worker function to search for passwords in a thread-safe manner."""
    found_passwords = manager.search_partial_passwords(search_string)
    with lock:  # Ensure thread-safe access to results
        results.extend(found_passwords)


def find_strings_containing_substring(substring, strings_set):
    return [s for s in strings_set if substring in s]


def check_exact_string(target_string, strings_set):
    return target_string in strings_set


def get_password_file_paths(specified_paths: str) -> List[str]:
    """Prompt the user to enter file paths for loading known passwords."""

    password_file_paths_input = specified_paths
    return [path.strip() for path in password_file_paths_input.split(',')] if password_file_paths_input else []


def get_password_file_paths_predetermined(path: str) -> List[str]:
    """Prompt the user to enter file paths for loading known passwords."""
    password_file_paths_input = path
    return [path.strip() for path in password_file_paths_input.split(',')] if password_file_paths_input else []


def get_password_set() -> Set[str]:
    """Prompt the user to enter a set of passwords."""
    password_set_input = input("Enter a set of passwords separated by commas (or leave blank to skip): ")
    return set(password_set_input.split(',')) if password_set_input else set()


# -------------------------------------------------------------------
# Statical analysis section

class BaseComplexity:
    def __init__(self, init_pass: str):
        self.init_pass = init_pass
        self.character_set_size = 94  # 26 lowercase + 26 uppercase + 10 digits + 32 special characters

    def calculate_entropy(self, password: str) -> float:
        """Calculate the entropy of the password."""
        length = len(password)
        unique_chars = len(set(password))
        if unique_chars == 0:
            return 0
        char_count = Counter(password)
        probabilities = [count / length for count in char_count.values()]
        entropy = -sum(p * math.log2(p) for p in probabilities)
        return entropy

    def standardize_entropy(self, entropy: float) -> float:
        min_entropy = 0
        max_entropy = 6
        standardized_entropy = (entropy - min_entropy) / (max_entropy - min_entropy)
        return max(0, min(1, standardized_entropy)) * 10  # Ensure the value is within [0, 1]

    def calculate_compliance_score(self, password: str) -> float:
        """Check compliance with OWASP and NIST regex standards."""
        # NIST and OWASP password requirements
        regex = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+[\]{};":\\|,.<>?]).{8,}$'

        # Check compliance
        if re.match(regex, password):
            return 10  # Fully compliant
        return 0  # Not compliant


class ActualSecurity:
    def __init__(self, init_pass: str, base_complexity: float, pass_hits: int):
        self.init_pass = init_pass
        self.base_complexity = base_complexity
        self.pass_hits = pass_hits

    def calculate_crackability_score(self, password: str, password_hits: int,
                                     common_hit: Optional[int] = None) -> float:
        """Calculate the crackability score based on password hits and MD5 hash."""
        # Calculate entropy

        # Calculate the MD5 hash (not used in the score calculation)
        md5_hash = hashlib.md5(password.encode()).hexdigest()

        # Calculate the number of hits
        num_hits = password_hits
        if common_hit is not None:
            com_hits = common_hit
        else:
            com_hits = 0

        # Define a penalty factor for the number of hits
        penalty_factor = 0.0
        common_penalty = 0.0

        if com_hits is not None:
            common_penalty = com_hits * 0.10

        if num_hits > 0:
            penalty_factor = 0.5  # 50% reduction for each hit
        if num_hits == 1:
            penalty_factor = 1.0  # Full reduction for a single hit
        else:
            penalty_factor = min(0.5 * (num_hits - 1), 1.0)  # 50% reduction for more than 2 hits, capped at 1.0

        # Calculate the crackability score
        crackability_score = 1 - ((num_hits * penalty_factor) + (common_hit * common_penalty))

        # Adjust the score to go into negatives if more than 2 hits
        if num_hits > 2:
            crackability_score -= (num_hits - 2) * 0.5  # Additional penalty for each hit beyond 2

        return crackability_score * 10

    def calculate_weighted_average(self, scores: List[float]) -> float:
        """Calculate a weighted average of the scores."""
        total_weight = sum(scores)
        return total_weight

    def calculate_overall_complexity(self, password: str, password_hits: int, com_hit: int) -> float:
        """Calculate the overall complexity score based on base complexity and actual security."""
        # Calculate base complexity scores
        base_complexity = BaseComplexity(self.init_pass)
        entropy_score = base_complexity.calculate_entropy(password)
        standardized_entropy = base_complexity.standardize_entropy(entropy_score)
        compliance_score = base_complexity.calculate_compliance_score(password)

        # Calculate MD5 resistance score
        md5_resistance = PasswordScorerMD5Measure().get_password_score(password)

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

    def example_usage(self, password_input: str, password_hits: int):
        # Example usage
        password = password_input
        base_complexity = BaseComplexity(password)
        base_entropy = base_complexity.calculate_entropy(password)
        base_standard_entropy = base_complexity.standardize_entropy(base_entropy)
        base_compliance = base_complexity.calculate_compliance_score(password)

        print(f"Base Complexity - Entropy: {base_entropy:.2f}")
        print(f"Base Complexity - Standard Entropy: {base_standard_entropy:.2f}")
        print(f"Base Complexity - Compliance: {base_compliance:.2f}")

        # Calculate actual security
        actual_security = ActualSecurity(password, base_entropy, password_hits)
        actual_crackability_score = actual_security.calculate_crackability_score(password, password_hits)
        md5_resistance = PasswordScorerMD5Measure().get_password_score(password)

        print(f"Actual Security - Crackability Score: {actual_crackability_score:.2f}")
        print(f"MD5 Resistance Score: {md5_resistance:.2f}")

        # Calculate overall complexity
        overall_complexity = actual_security.calculate_overall_complexity(password, password_hits)

        print(f"Overall Complexity Score: {overall_complexity:.2f}")

        # Generate a strong password
        strong_password = self.generate_strong_password(length=12)
        print(f"Generated Strong Password: {strong_password}")
        print(
            f"Score for Generated Password: {ActualSecurity(strong_password, 0.0, 0).calculate_overall_complexity(0):.2f}")

        """
        # Write results to a unique text file
        file_name = f"password_analysis_results.txt"
        with open(file_name, 'w') as file:
            file.write(json.dumps({
                "Password": password,
                "Base Complexity - Entropy": base_entropy,
                "Base Complexity - Standard Entropy": base_standard_entropy,
                "Base Complexity - Compliance": base_compliance,
                "Actual Security - Crackability Score": actual_crackability_score,
                "MD5 Resistance Score": md5_resistance,
                "Overall Complexity Score": overall_complexity,
                "Generated Strong Password": strong_password,
                "Score for Generated Password": ActualSecurity(strong_password, 0.0, 0).calculate_overall_complexity(0)
            }, indent=4))
        """
        return overall_complexity

    def generate_strong_password(self, length: int = 14) -> str:
        """Generate a strong password that meets complexity requirements."""
        if length < 8:
            raise ValueError("Password length should be at least 8 characters.")

        # Ensure the password contains at least one lowercase, one uppercase, one digit, and one special character
        lower = random.choice(string.ascii_lowercase)
        upper = random.choice(string.ascii_uppercase)
        digit = random.choice(string.digits)
        special = random.choice(string.punctuation)

        # Fill the rest of the password length with random choices from all character sets
        all_characters = string.ascii_letters + string.digits + string.punctuation
        remaining_length = length - 4  # 4 characters already chosen

        # Generate the remaining characters
        password = lower + upper + digit + special + ''.join(
            random.choice(all_characters) for _ in range(remaining_length))

        # Shuffle the password to ensure randomness
        password_list = list(password)
        random.shuffle(password_list)
        return ''.join(password_list)


class PasswordScorerMD5Measure:
    def __init__(self):
        # Define regex patterns for different password structures
        self.nums_only = re.compile(r'^\d+$')
        self.lower_only = re.compile(r'^[a-z]+$')
        self.uplow = re.compile(r'^[a-zA-Z]+$')
        self.num_uplow = re.compile(r'^[a-zA-Z0-9]+$')
        self.num_uplow_symbols = re.compile(r'^[a-zA-Z0-9!@#$%^&*()_+[\]{};":\\|,.<>?]+$')

        # Define the score mapping based on the table
        self.score_mapping = {
            'Nums only': {
                8: 0, 9: 0, 10: 0, 11: 0, 12: 0, 13: 0, 14: 0, 15: 0,
                16: 0, 17: 0, 18: 0.1, 19: 0.2, 20: 0.3, 21: 0.5, 22: 0.8, 23: 1.0
            },
            'Lower only': {
                8: 0, 9: 0, 10: 0, 11: 0, 12: 0, 13: 0.4, 14: 1, 15: 1, 16: 1,
                17: 1, 18: 1, 19: 1, 20: 1, 21: 1, 22: 1
            },
            'Uplow': {
                8: 0, 9: 0, 10: 0, 11: 0.3, 12: 0.4, 13: 1, 14: 1, 15: 1, 16: 1,
                17: 1, 18: 1, 19: 1, 20: 1, 21: 1, 22: 1
            },
            'Num+uplow': {
                8: 0, 9: 0, 10: 0.2, 11: 0.3, 12: 1, 13: 1, 14: 1, 15: 1, 16: 1,
                17: 1, 18: 1, 19: 1, 20: 1, 21: 1, 22: 1
            },
            'Num+uplow w+symbols': {
                8: 0, 9: 0.2, 10: 0.3, 11: 1, 12: 1, 13: 1, 14: 1, 15: 1, 16: 1,
                17: 1, 18: 1, 19: 1, 20: 1, 21: 1, 22: 1
            }
        }

    def get_password_score(self, password: str) -> float:
        length = len(password)

        # Determine the structure of the password
        if self.nums_only.match(password):
            structure = 'Nums only'
        elif self.lower_only.match(password):
            structure = 'Lower only'
        elif self.uplow.match(password):
            structure = 'Uplow'
        elif self.num_uplow.match(password):
            structure = 'Num+uplow'
        elif self.num_uplow_symbols.match(password):
            structure = 'Num+uplow w+symbols'
        else:
            structure = 'Num+uplow w+symbols'

        # Get the score based on the length and structure
        score = self.score_mapping.get(structure, {}).get(length, 0)
        if (len(password) > 22):
            score = 1
        return score * 10

    def calculate_entropy(self, password: str) -> float:
        """Calculate the entropy of the password."""
        length = len(password)
        unique_chars = len(set(password))
        if unique_chars == 0:
            return 0
        char_count = Counter(password)
        probabilities = [count / length for count in char_count.values()]
        entropy = -sum(p * math.log2(p) for p in probabilities)
        return entropy

    def calculate_compliance_score(self, password: str) -> float:
        """Check compliance with OWASP and NIST regex standards."""
        # NIST and OWASP password requirements
        regex = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()_+[\]{};":\\|,.<>?]).{8,}$'

        # Check compliance
        if re.match(regex, password):
            return 10  # Fully compliant
        return 0  # Not compliant

    def calculate_crackability_score(self, password: str, password_hits: int) -> float:
        """Calculate the crackability score based on password hits and MD5 hash."""
        # Calculate entropy
        entropy = self.calculate_entropy(password)
        standardized_entropy = BaseComplexity("").standardize_entropy(entropy)

        # Calculate the number of hits
        num_hits = password_hits

        # Define a penalty factor for the number of hits
        penalty_factor = 0
        if num_hits > 0:
            if num_hits == 1:
                penalty_factor = 1.0  # Full reduction for a single hit
            else:
                penalty_factor = (1 + (0.2 * num_hits))

        # Calculate the crackability score
        crackability_score = (num_hits * penalty_factor)
        return crackability_score

    def calculate_weighted_average(self, scores: List[float]) -> float:
        """Calculate a weighted average of the scores."""
        total_weight = sum(scores)
        return total_weight

    def calculate_overall_complexity(self, password: str, password_hits: int) -> float:
        """Calculate the overall complexity score based on base complexity and actual security."""
        # Calculate base complexity scores
        base_complexity = BaseComplexity(password)
        entropy_score = base_complexity.calculate_entropy(password)
        standardized_entropy = base_complexity.standardize_entropy(entropy_score)
        compliance_score = base_complexity.calculate_compliance_score(password)

        # Calculate crackability score
        crackability_score = self.calculate_crackability_score(password, password_hits)

        w_e = 0.3
        w_c = 0.2
        w_cr = 0.4
        # Combined score
        overall_complexity_score = self.calculate_weighted_average(
            [standardized_entropy * w_e,
             compliance_score * w_c,
             crackability_score * w_cr]
        )

        return overall_complexity_score

    def example_usage(self, password_input: str, password_hits: int, com_hit: None) -> str:
        # Example usage
        result_stats = []
        password = password_input
        base_complexity = BaseComplexity(password)
        base_entropy = base_complexity.calculate_entropy(password)
        base_standard_entropy = base_complexity.standardize_entropy(base_entropy)
        base_compliance = base_complexity.calculate_compliance_score(password)
        pass_score = self.get_password_score(password)
        result_stats.append(f"\nBase Complexity - Entropy: {base_entropy:.2f}")
        result_stats.append(f"\nBase Complexity - Standard Entropy: {base_standard_entropy:.2f}")
        result_stats.append(f"\nBase Complexity - Compliance: {base_compliance:.2f}")
        result_stats.append(f"\nPassword MD5 resistance score: {pass_score:.2f}")

        # Calculate actual security
        actual_security = ActualSecurity(password, base_entropy, password_hits)
        actual_crackability_score = actual_security.calculate_crackability_score(password, password_hits, com_hit)


        result_stats.append(f"\nActual Security - Crackability Score: {actual_crackability_score:.2f}")
        # Calculate overall complexity
        overall_complexity = actual_security.calculate_overall_complexity(password, password_hits, com_hit)
        result_stats.append(f"\nOverall Complexity Score: {overall_complexity:.2f}")
        if overall_complexity < 4.746:
            result_stats.append(f"\n weak password!")
        elif 4.746 <= overall_complexity <= 8.64:
            result_stats.append(f"\n average password")
        else:
            result_stats.append(f"\n strong password")


        # Generate a strong password
        strong_password = self.generate_strong_password(length=12)
        result_stats.append(f"\nGenerated Strong Password: {strong_password}")
        final_stats = "".join(result_stats)
        return final_stats

    def generate_strong_password(self, length: int = 12) -> str:
        """Generate a strong password that meets complexity requirements."""
        if length < 8:
            raise ValueError("Password length should be at least 8 characters.")

        # Ensure the password contains at least one lowercase, one uppercase, one digit, and one special character
        lower = random.choice(string.ascii_lowercase)
        upper = random.choice(string.ascii_uppercase)
        digit = random.choice(string.digits)
        special = random.choice(string.punctuation)

        # Fill the rest of the password length with random choices from all character sets
        all_characters = string.ascii_letters + string.digits + string.punctuation
        remaining_length = length - 4  # 4 characters already chosen

        # Generate the remaining characters
        password = lower + upper + digit + special + ''.join(
            random.choice(all_characters) for _ in range(remaining_length))

        # Shuffle the password to ensure randomness
        password_list = list(password)
        random.shuffle(password_list)
        return ''.join(password_list)


def score_password_complexity(passwords: set[str], password_hits: int, com_hit: None) -> float:
    """Score the complexity of a set of passwords and return the highest scoring password."""
    highest_score = 0.0
    best_password = ""

    for password in passwords:
        base_complexity = BaseComplexity(password)
        entropy_score = base_complexity.calculate_entropy(password)
        standardized_entropy = base_complexity.standardize_entropy(entropy_score)
        compliance_score = base_complexity.calculate_compliance_score(password)

        # Calculate actual security
        actual_security = ActualSecurity(password, entropy_score, password_hits)
        md5_resistance = PasswordScorerMD5Measure().get_password_score(password)
        crackability_score = actual_security.calculate_crackability_score(password, password_hits, com_hit)

        # Calculate overall complexity score
        overall_complexity_score = actual_security.calculate_overall_complexity(password, password_hits, 0)

        if overall_complexity_score > highest_score:
            highest_score = overall_complexity_score
            best_password = password

    return highest_score, best_password


# --------------------------------------------
# Leet speak character substitution section
import random
import hashlib
from typing import Dict, List, Set
from concurrent.futures import ThreadPoolExecutor


def capital(word, state):
    match state:
        case 'u':
            text = list(word)
            if text[0].isalpha():
                return word.capitalize()
            else:
                return word
        case 'lu':
            text = list(word)
            if text[-1].isalpha():
                text[-1] = text[-1].upper()
                return ''.join(text)
            else:
                return word
        case 'bu':
            text = list(word)
            if text[0].isalpha() and text[-1].isalpha():
                text[0] = text[0].upper()
                text[-1] = text[-1].upper()
                return ''.join(text)
            else:
                return word


def repeatWord(word, num):
    return word * num


class AdvancedLeetSpeakConverter:
    def __init__(self, leet_map):
        self.leet_map = leet_map
        self.conversion_strategies = {
            'rand': self._random_replacement,
            'first': self._first_replacement,
            'last': self._last_replacement,
            'comprehensive': self._comprehensive_replacement,
            'choose': self._choose_replacement
        }

    def _random_replacement(self, char):
        char_seed = int(hashlib.md5(char.encode()).hexdigest(), 16)
        char_rng = random.Random(char_seed)
        replacements = self.leet_map.get(char.lower(), [char])
        return char_rng.choice(replacements)

    def _first_replacement(self, char):
        replacements = self.leet_map.get(char, [char])
        return replacements[0]

    def _last_replacement(self, char):
        replacements = self.leet_map.get(char, [char])
        return replacements[-1]

    def _choose_replacement(self, char, num):
        replacements = self.leet_map.get(char, [char])
        if num <= len(replacements) - 1:
            return replacements[num]
        else:
            return replacements[-1]

    def _comprehensive_replacement(self, char):
        replacements = self.leet_map.get(char.lower(), [char])
        if char.isupper():
            replacement = random.choice(replacements)
            return replacement.upper() if len(replacement) == 1 else replacement
        return random.choice(replacements)

    def convert(self, text, strategy='rand', replace_count=None, positions=None, num_rep=None):
        conversion_method = self.conversion_strategies.get(strategy, self._random_replacement)
        chars = list(text)

        if positions is None:
            if replace_count is None:
                replace_positions = list(range(len(chars)))
            else:
                replace_positions = random.sample(range(len(chars)), min(replace_count, len(chars)))
        else:
            replace_positions = [pos for pos in positions if 0 <= pos < len(chars)]

        if replace_count is not None:
            replace_positions = replace_positions[:replace_count]

        for pos in replace_positions:
            char = chars[pos]
            if strategy == 'choose':
                if num_rep is None:
                    raise ValueError("num_rep must be provided when using 'choose' strategy.")
                replacement = self._choose_replacement(char, num_rep)
            else:
                replacement = conversion_method(char)
            chars[pos] = replacement

        return ''.join(chars)

    def multi_variant_convert(self, text, num_variants=3, replace_count=None, positions=None):
        variants = []
        for _ in range(num_variants):
            strategies = ['rand', 'first', 'last', 'comprehensive']
            strategy = random.choice(strategies)
            variant = self.convert(text, strategy=strategy, replace_count=replace_count, positions=positions)
            variants.append(variant)
        return variants

    def generate_replacement_patterns(self, text, num_patterns=3):
        patterns = []
        for _ in range(num_patterns):
            max_replacements = len(text)
            replace_count = random.randint(1, max_replacements)
            pattern = {
                'replace_count': replace_count,
                'positions': random.sample(range(len(text)), replace_count),
                'strategy': random.choice(list(self.conversion_strategies.keys()))
            }
            patterns.append(pattern)
        return patterns


def generate_all_leet_variants(converter: AdvancedLeetSpeakConverter, text: str, num_variants_per_strategy: int = 5):
    variants = []
    unique_variants = set()
    text_length = len(text)

    for strategy in converter.conversion_strategies.keys():
        for _ in range(num_variants_per_strategy):
            positions = random.sample(range(text_length), random.randint(1, text_length))
            if strategy == 'choose':
                variant = text
                for pos in positions:
                    replacements = converter.leet_map.get(text[pos].lower(), [text[pos]])
                    num_rep = random.randint(0, len(replacements) - 1)
                    replacement = replacements[num_rep]
                    variant = variant[:pos] + replacement + variant[pos + 1:]
            else:
                variant = converter.convert(text, strategy=strategy, replace_count=len(positions), positions=positions)
                unique_variants.add(variant)
                variants.append(variant)
    return variants


def cap_word(password: str, state: str):
    return capital(password, state)


def repeat_word(password: str, repNum: int):
    return repeatWord(password, repNum)


def leet_replace_basic(comprehensive_leet_map: Dict[str, List[str]], password: str, strat: str, rep_count: int,
                       pos: int, num_repeat: int):
    converter = AdvancedLeetSpeakConverter(comprehensive_leet_map)
    return converter.convert(password, strat, rep_count, [pos], num_repeat)


def comprehensive_replace_leet(comprehensive_leet_map: Dict[str, List[str]], password: str, variant_seed: int):
    converter = AdvancedLeetSpeakConverter(comprehensive_leet_map)
    unique_variants = set()

    rand_variant = converter.convert(password, 'rand', 1)
    comp_variant = converter.convert(password, 'comprehensive', 1)
    first_variant = converter.convert(password, 'first', 1)
    last_variant = converter.convert(password, 'last', 1)

    for i in range(len(password)):
        choose_variant = converter.convert(password, 'choose', 2, [i], 1)
        unique_variants.add(choose_variant)

    unique_variants.add(rand_variant)
    unique_variants.add(comp_variant)
    unique_variants.add(first_variant)
    unique_variants.add(last_variant)

    leet_variants = set()

    def generate_variants(variant):
        generated_leet_variants = generate_all_leet_variants(converter, variant,
                                                             num_variants_per_strategy=variant_seed * 10)
        for leet_variant in generated_leet_variants:
            if leet_variant not in leet_variants:
                leet_variants.add(leet_variant)

    with ThreadPoolExecutor() as executor:
        executor.map(generate_variants, unique_variants)

    return leet_variants


class PasswordCheckerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Password Checker")
        self.root.geometry("600x500")

        self.expanded = False
        self.create_widgets()

    def create_widgets(self):
        # Variant Path
        ttk.Label(self.root, text="Variant Path:").grid(column=0, row=0, sticky=tk.W, padx=10, pady=10)
        self.variant_path_entry = ttk.Entry(self.root, width=50)
        self.variant_path_entry.grid(column=1, row=0, padx=10, pady=10)
        ttk.Button(self.root, text="Browse", command=self.browse_variant_path).grid(column=2, row=0, padx=10, pady=10)

        # Checkbox for Variant Check
        self.check_variants_var = tk.BooleanVar()
        ttk.Checkbutton(self.root, text="Check Variants", variable=self.check_variants_var).grid(column=1, row=1,
                                                                                                 pady=10)

        # Common Passwords Path
        ttk.Label(self.root, text="Common Passwords Path:").grid(column=0, row=2, sticky=tk.W, padx=10, pady=10)
        self.common_passwords_path_entry = ttk.Entry(self.root, width=50)
        self.common_passwords_path_entry.grid(column=1, row=2, padx=10, pady=10)
        ttk.Button(self.root, text="Browse", command=self.browse_common_passwords_path).grid(column=2, row=2, padx=10,
                                                                                             pady=10)

        # Wordlist Path
        ttk.Label(self.root, text="Wordlist Path:").grid(column=0, row=3, sticky=tk.W, padx=10, pady=10)
        self.wordlist_path_entry = ttk.Entry(self.root, width=50)
        self.wordlist_path_entry.grid(column=1, row=3, padx=10, pady=10)
        ttk.Button(self.root, text="Browse", command=self.browse_wordlist_path).grid(column=2, row=3, padx=10, pady=10)

        # Password Field
        ttk.Label(self.root, text="Password:").grid(column=0, row=4, sticky=tk.W, padx=10, pady=10)
        self.password_entry = ttk.Entry(self.root, width=50, show="*")
        self.password_entry.grid(column=1, row=4, padx=10, pady=10)

        # Check Password Button
        ttk.Button(self.root, text="Check Password", command=self.check_password).grid(column=1, row=5, pady=20)

        # Scrollable Textbox for Results
        self.result_textbox = scrolledtext.ScrolledText(self.root, wrap=tk.WORD, width=70, height=10)
        self.result_textbox.grid(column=0, row=6, columnspan=3, padx=10, pady=10)

        # Expand/Collapse Button
        ttk.Button(self.root, text="Expand Results", command=self.toggle_expanded).grid(column=1, row=7, pady=20)

        # Generic Pop-up Button
        ttk.Button(self.root, text="Show Pop-up",
                   command=lambda: self.show_generic_popup("This is a custom message!")).grid(column=1, row=8, pady=20)

        # Variant Pop-up Button
        ttk.Button(self.root, text="Show Variant Pop-up", command=self.show_variant_popup).grid(column=1, row=9,
                                                                                                pady=20)

    def browse_variant_path(self):
        path = filedialog.askopenfilename()
        if path:
            self.variant_path_entry.delete(0, tk.END)
            self.variant_path_entry.insert(0, path)


    def display_result(self, result):
        self.result_textbox.insert(tk.END, result + "\n")


    def browse_common_passwords_path(self):
        path = filedialog.askopenfilename()
        if path:
            self.common_passwords_path_entry.delete(0, tk.END)
            self.common_passwords_path_entry.insert(0, path)

    def browse_wordlist_path(self):
        path = filedialog.askopenfilename()
        if path:
            self.wordlist_path_entry.delete(0, tk.END)
            self.wordlist_path_entry.insert(0, path)

    def check_password(self):
        variant_path = self.variant_path_entry.get()
        check_variants = self.check_variants_var.get()
        common_passwords_path = self.common_passwords_path_entry.get()
        wordlist_path = self.wordlist_path_entry.get()
        password = self.password_entry.get()

        # Perform password checking logic here
        self.perform_password_check(check_variants, variant_path, common_passwords_path, wordlist_path,
                                             password)

        # Display the result in the scrollable textbox


    def perform_password_check(self, check_variants, variant_path, common_passwords_path, wordlist_path, password):
        # Clear previous input
        self.result_textbox.delete(1.0, tk.END)

        # Placeholder for password checking logic
        # Define variables
        chunks_per_shard = (4, 4)  # 4x4 chunks
        manager = ShardingStorageTransformer("indexed", chunks_per_shard)
        p_hits = 0
        c_hits = 0
        password_hits = 0
        common_hit = 0

        # Define Map for character substitution:
        comprehensive_leet_map = {
            'a': ['@', '4', '/\\', '^'],
            'e': ['3'],
            'i': ['1', '!', '|'],
            'o': ['0', '()', '[]'],
            'u': ['(_)', 'v'],
            'b': ['8', '13', '|3'],
            'g': ['6', '9', '&'],
            's': ['$', '5', 'z'],
            't': ['7', '+'],
            'l': ['1'],
            'z': ['2', '%'],
            '1': ['!', 'i'],
            '0': ['o', '()'],
        }
        final_result_parts = []

        # Get file paths and password set from the user
        common_passwords_path = COMMON_PASSWORD_PATH
        password_file_paths = get_password_file_paths(common_passwords_path)

        # Load known passwords from the specified files and set
        password_file_paths.append(wordlist_path)
        manager.load_known_passwords(password_file_paths, None)

        # Get the number of known passwords
        known_passwords_count = manager.get_known_passwords_count()
        final_result_parts.append(f"Loaded {known_passwords_count} known passwords.")

        # Define the search string
        # Start the search and measure the time taken
        start_time = time.time()
        exact_match = manager.chunk_shard_search(password)
        partial_match = manager.search_partial_passwords(password)
        elapsed_time = time.time() - start_time
        final_result_parts.append(f"\nTime elapsed: {elapsed_time}")

        if exact_match:
            final_result_parts.append(f"\nExact match found: {exact_match}")
            p_hits += 1
        else:
            final_result_parts.append("\nNo exact match found.")

        final_result_parts.append(f"\nPartial matches with a length of {len(partial_match)}")
        p_hits += len(partial_match) * 0.25

        manager.clear_known_passwords()
        common_choice = check_variants
        if common_choice == True:
            if variant_path is None:
                path_common = get_password_file_paths_predetermined(COMMON_PATTERNS_PATH)
            else:
                path_common = get_password_file_paths_predetermined(variant_path)
            manager.load_known_passwords(path_common)
            exact_match_common = manager.chunk_shard_search(password)
            partial_match_common = manager.search_partial_passwords(password)
            final_result_parts.append(f"\nTime elapsed: {elapsed_time}")

            if exact_match_common:
                final_result_parts.append(f"\nExact common match found: {exact_match_common}")
                c_hits += 1
            else:
                final_result_parts.append("No exact common match found.")
            c_hits += len(partial_match_common)

        


        # Usage of password complexity stat analysis
        password_input = password
        encoded_password = urllib.parse.quote_plus(password_input)
        password_hits = p_hits
        common_hit = c_hits
        password_scorer = PasswordScorerMD5Measure()
        stats = password_scorer.example_usage(encoded_password, password_hits, common_hit)
        final_result_parts.append(f"{stats}")
        self.display_result("\n")

        # Example usage of password complexity with variants
        leet_variants = comprehensive_replace_leet(comprehensive_leet_map, password, 1)
        password_set = leet_variants
        password_hits = 0
        common_hit = 0

        highest_score, best_password = score_password_complexity(password_set, password_hits, common_hit)
        final_result_parts.append(f"\nHighest Scoring Password Statistically: {best_password}")

        final_result_parts.append(f"\nComplexity Score: {highest_score:.2f}")

        final_result = "".join(final_result_parts)
        print(final_result)
        self.display_result(final_result)

        # Clear the known passwords list for the next search
        manager.clear_known_passwords()

    def toggle_expanded(self):
        self.expanded = not self.expanded
        self.update_layout()

    def update_layout(self):
        if self.expanded:
            # Expand the results textbox to full screen
            self.result_textbox.config(width=100, height=30)
            self.root.geometry("1000x800")
        else:
            # Collapse the results textbox to original size
            self.result_textbox.config(width=70, height=10)
            self.root.geometry("600x500")

    def show_generic_popup(self, message):
        # Debug output
        print("Showing generic pop-up with message:", message)
        messagebox.showinfo("Custom Pop-up", message)

    def show_variant_popup(self):
        # Debug output
        print("Showing variant pop-up")

        def check_variants():
            messagebox.showinfo("Variants", "Variants checked successfully!")

        popup = tk.Toplevel(self.root)
        popup.title("Variant Pop-up")
        popup.geometry("300x200")

        ttk.Label(popup, text="Enter your message:").pack(pady=10)
        message_entry = ttk.Entry(popup, width=50)
        message_entry.pack(pady=10)

        ttk.Button(popup, text="Check Variants", command=check_variants).pack(pady=10)

        variants_text = tk.Text(popup, wrap=tk.WORD, width=30, height=5)
        variants_text.pack(pady=10)
        variants_text.insert(tk.END, "Variants will be displayed here.")


if __name__ == "__main__":
    root = tk.Tk()
    app = PasswordCheckerApp(root)
    root.mainloop()
