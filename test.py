import random
from time import sleep



def test_complete(model, messages):

    lorem_ipsum_words = [
        "lorem", "ipsum", "dolor", "sit", "amet", "consectetur",
        "adipiscing", "elit", "sed", "do", "eiusmod", "tempor",
        "incididunt", "ut", "labore", "et", "dolore", "magna",
        "aliqua", "ut", "enim", "ad", "minim", "veniam", "quis",
        "nostrud", "exercitation", "ullamco", "laboris", "nisi",
        "ut", "aliquip", "ex", "ea", "commodo", "consequat"
    ]

    # Randomly select 20 words from the lorem_ipsum_words list
    random_words = random.sample(lorem_ipsum_words, 20)

    # Join the selected words into a single string
    random_lorem_ipsum = ' '.join(random_words)

    # Yield the generated string
    yield random_lorem_ipsum
