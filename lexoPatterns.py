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
        generated_leet_variants = generate_all_leet_variants(converter, variant, num_variants_per_strategy=variant_seed * 10)
        for leet_variant in generated_leet_variants:
            if leet_variant not in leet_variants:
                leet_variants.add(leet_variant)

    with ThreadPoolExecutor() as executor:
        executor.map(generate_variants, unique_variants)

    for i, leet_variant in enumerate(leet_variants):
        print( f"leet variant {i} {leet_variant}")
    return leet_variants

def main():

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

    password = input("Enter the password to generate: ")
    leet_variants = comprehensive_replace_leet(comprehensive_leet_map, password, 1)

if __name__ == "__main__":
    main()
