import random
from time import sleep

def test_complete(model, messages, image_data=None):
    lorem_ipsum_words = [
        "lorem", "ipsum", "dolor", "sit", "amet", "consectetur",
        "adipiscing", "elit", "sed", "do", "eiusmod", "tempor",
        "incididunt", "ut", "labore", "et", "dolore", "magna",
        "aliqua", "ut", "enim", "ad", "minim", "veniam", "quis",
        "nostrud", "exercitation", "ullamco", "laboris", "nisi",
        "ut", "aliquip", "ex", "ea", "commodo", "consequat"
    ]

    for i in range(20):

        # Randomly select 20 words from the lorem_ipsum_words list
        random_lorem_ipsum = random.choice(lorem_ipsum_words)
        sleep(0.1)
        # Yield the generated string
        yield random_lorem_ipsum
