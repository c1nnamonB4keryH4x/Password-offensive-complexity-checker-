# Define the patterns
patterns = {
    "mixed_patterns": [
        "qwerty123456", "asdfgh123456", "zxcvbn123456", "qwerty!@#",
        "asdfgh!@#", "zxcvbn!@#", "qwerty123!@#", "asdfgh123!@#",
        "zxcvbn123!@#"
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
    "keyboard_patterns": {
        "horizontal_patterns": [
            "qwerty", "asdf", "zxcv", "qwertyuiop", "asdfgh", "qazwsx",
            "123456", "123456789", "qwerty123", "asdf123", "zxcvbnm",
            "qwertyui", "asdfghjkl", "qwertyuiopasdf", "12345678"
        ],
        "vertical_patterns": [
            "qaz", "wsx", "edc", "rfv", "tgb", "yhn", "ujm",
            "ik,", "ol.", "p;/", "123", "456", "789", "0-="
        ],
        "diagonal_patterns": [
            "rfv", "tgb", "yhn", "ujm", "ik,", "ol."
        ],
        "combinations_of_letters_and_numbers": [
            "qwerty123", "asdf123", "zxcvbn123", "qwertyui", "asdfgh",
            "qwertyuiop123", "1234567890", "qwertyuiopasdfghjkl",
            "qwertyuiopasdfghjklzxcvbnm", "qwertyuiopasdfghjkl;"
        ],
        "extended_patterns": [
            "qwertyuiopasdfghjklzxcvbnm1234567890",
            "qwertyuiopasdfghjklzxcvbnm!@#$%^&*()",
            "qwertyuiopasdfghjklzxcvbnm,./;'[]",
            "qwertyuiopasdfghjklzxcvbnm<>?:\"{}|"
        ],
        "patterns_with_special_characters": [
            "qwertyuiopasdfghjklzxcvbnm1234567890!@#$%^&*()",
            "qwertyuiopasdfghjklzxcvbnm!@#$%^&*()_+",
            "qwertyuiopasdfghjklzxcvbnm1234567890-=~",
            "qwertyuiopasdfghjklzxcvbnm!@#$%^&*()_+[]{}",
            "qwertyuiopasdfghjklzxcvbnm!@#$%^&*()_+<>?"
        ],
        "additional_patterns": [
            "qwertyuiopasdfghjklzxcvbnm1234567890!@#$%^&*()_+<>?",
            "qwertyuiopasdfghjklzxcvbnm!@#$%^&*()_+[]{}",
            "qwertyuiopasdfghjklzxcvbnm1234567890-=~",
            "qwertyuiopasdfghjklzxcvbnm!@#$%^&*()_+<>?"
        ],
        "repeated_patterns": [
            "qwertyqwerty", "asdfasdf", "zxcvzxcv", "123123", "456456",
            "789789", "qwertyuiopqwertyuiop", "asdfghjklasdfghjkl"
        ]
    },
    "sequential_characters": [
        "zxcv", "1234", "abcd", "efgh", "ijkl", "mnop", "qrst", "uvwx", "yz"
    ],
    "common_substitutions": [
        "p@ssw0rd", "l3tme1n", "w3lc0me", "adm1n", "u53r", "t3st",
        "abc!23", "il0veu", "m0nkey", "dr@gon", "sun$hine",
        "qw3rty", "f00tball", "b@s3ball", "trusTn01", "iloveyou123", "0penme"
    ]
}


# Function to write patterns to a text file
def write_patterns_to_file(patterns, filename='patterns.txt'):
    with open(filename, 'w') as file:
        for category, items in patterns.items():
            file.write(f"{category}:\n")
            if isinstance(items, dict):  # Handle nested dictionaries
                for subcategory, subitems in items.items():
                    file.write(f"  {subcategory}:\n")
                    for item in subitems:
                        file.write(f"     {item}\n")
            else:  # Handle lists
                for item in items:
                    file.write(f" {item}\n")
            file.write("\n")  # Add a newline for better readability


# Write the patterns to the file
write_patterns_to_file(patterns)

print("Patterns have been written to patterns.txt.")
