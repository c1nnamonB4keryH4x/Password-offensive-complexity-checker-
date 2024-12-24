import threading
import time
from typing import NamedTuple, Tuple, Optional, Union, List, Iterator, Set
import math
from functools import reduce
from operator import mul

MAX_UINT_64 = 2 ** 64 - 1

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

def get_password_file_paths() -> List[str]:
    """Prompt the user to enter file paths for loading known passwords."""
    password_file_paths_input = input("Enter the paths to the password files separated by commas (or leave blank to skip): ")
    return [path.strip() for path in password_file_paths_input.split(',')] if password_file_paths_input else []

def get_password_set() -> Set[str]:
    """Prompt the user to enter a set of passwords."""
    password_set_input = input("Enter a set of passwords separated by commas (or leave blank to skip): ")
    return set(password_set_input.split(',')) if password_set_input else set()

def main():
    # Define the path and chunk configuration
    chunks_per_shard = (4, 4)  # 4x4 chunks
    # Create an instance of ShardingStorageTransformer
    manager = ShardingStorageTransformer("indexed", chunks_per_shard)

    while True:
        # Get file paths and password set from the user
        password_file_paths = get_password_file_paths()
        password_set = get_password_set()

        # Load known passwords from the specified files and set
        manager.load_known_passwords(password_file_paths, password_set)

        # Get the number of known passwords
        known_passwords_count = manager.get_known_passwords_count()
        print(f"Loaded {known_passwords_count} known passwords.")

        # Define the search string
        search_string = input("Enter the string to search for in the known passwords: ")

        # Start the search and measure the time taken
        start_time = time.time()
        # Perform the search in the known passwords
        exact_match = manager.chunk_shard_search(search_string)
        partial_match = manager.search_partial_passwords(search_string)
        # Measure the time taken for the search
        elapsed_time = time.time() - start_time
        # Display the results
        print(f"Time elapsed: {elapsed_time}")
        if exact_match:
            print(f"Exact match found: {exact_match}")
        else:
            print("No exact match found.")
        print(f"Partial matches: {partial_match}\n with a length of {len(partial_match)}")

        # Ask the user if they want to perform another search
        another_search = input("Do you want to perform another search? (yes/no): ").strip().lower()
        if another_search != 'yes':
            break

        # Clear the known passwords list for the next search
        manager.clear_known_passwords()

if __name__ == "__main__":
    main()
