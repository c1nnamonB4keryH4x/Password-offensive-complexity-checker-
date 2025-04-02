# Password-complexity-checker
Upon launching the tool, you will be greeted with a user-friendly interface that allows you to input passwords and configure settings for the evaluation process.
1. Using the Tool
Input Fields

    Variant Path: Enter the path to the variant file or click "Browse" to select it.
    Common Passwords Path: Enter the path to the common passwords file or click "Browse" to select it.
    Wordlist Path: Enter the path to the wordlist file or click "Browse" to select it.
    Password Entry: Input the password you wish to evaluate in the designated field.

Password Checking

    Check Password: Click the "Check Password" button to initiate the evaluation process.
    Options: You can choose to check variants by checking the "Check Variants" checkbox.

Viewing Results

    The results of the password evaluation will be displayed in a scrollable text box at the bottom of the interface.
    Results include:
        Loaded known passwords count
        Time taken for evaluation
        Exact and partial match findings
        Password complexity scores (entropy, compliance, crackability)
        Suggestions for strong passwords

2. Advanced Features
Loading Known Passwords

    The tool allows you to load known passwords from specified files. You can input multiple file paths separated by commas.
    The tool will attempt to load passwords from the provided paths and display the count of loaded passwords.

Generating Strong Passwords

    The tool can generate strong passwords that meet complexity requirements. You can specify the desired length for the generated password.
    Generated passwords will be displayed in the results section.

3. Troubleshooting

    Common Issues:
        File Not Found: Ensure that the paths entered for variant, common passwords, and wordlist files are correct.
        Encoding Errors: The tool attempts to load files using multiple encodings. If you encounter issues, check the file encoding.
        Performance Issues: If the tool is slow, consider optimizing the wordlist or reducing the number of passwords being checked.

4. FAQs
Q1: What types of passwords can I check?

A1: You can check any password, including common passwords, complex passwords, and passphrases.
Q2: How does the tool calculate password strength?

A2: The tool calculates password strength using metrics such as entropy, compliance with standards, and crackability scores based on known vulnerabilities.
Q3: Can I customize the wordlists used for evaluation?

A3: Yes, you can specify your own wordlists by providing the file paths in the input fields.

