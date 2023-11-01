import re
import sys
import time

chunks = []
stripped_text = "" # This var always holds the text without the previous chunks
break_markers = {
    'step1': ['.',';',':','!','?'],
    'step2': ['.',';',':','!','?'],
    'step3': [','],
    'step4': [' ']
}
chunks_ready = False
sys.setrecursionlimit(999999999)

def split_and_recombine_text(text, split_length):
    global stripped_text
    global chunks_ready
    global chunks

    chunks.clear()
    stripped_text = ""
    chunks_ready = False

    """Split text it into chunks of a desired length trying to keep sentences intact."""
    
    pattern = re.compile(r'[^a-zA-Z0-9?,%.:;!$ \n]') # Only keep these chars
    text = pattern.sub('', text) # replace everything that is not appoved chars with nothing
    text = re.sub(r"\n{3,}", "~", text)
    text = re.sub(r"\n{2}", "\n", text)
    text = re.sub(r"(?<!~)\n", "|", text)
    text = re.sub(r":", ",", text)
    text = re.sub(r";", "|", text)
    text = re.sub(r"\.{2,}", ".", text)
    text = re.sub(r",{2,}", ",", text)
    text = re.sub(r"\${2,}", "$", text)
    text = re.sub(r"\?{2,}", "?", text)
    text = re.sub(r"!{2,}", "!", text)
    text = re.sub(r"%{2,}", "%", text)
    text = re.sub(r"%", " percent", text)
    text = re.sub(r"\s+", " ", text)
    #print("\n---- Original:")
    #print(text)
    #print("--- Whle splitting, after filtering")
    stripped_text = text
    
    find_breakpoint(split_length)
    while(True):
        #print("\n---- Chunks detected:")
        if chunks_ready:
            #print(chunks)
            return chunks
        time.sleep(1)


def create_chunk(end,split_length):
    global chunks
    global stripped_text
    global break_markers

    #print("--- in func")
    # create chunk
    chunk = stripped_text[0:end+1]
    chunk = chunk.replace('\n',' ')
    chunk = chunk.strip()
    #print("----^^^^^-----Chunk list length1: " + str(len(chunks)))
    chunks.append(chunk)
    #print("----^^^^^-----Chunk list after1: " + str(len(chunks)))
    # remove chunk from text
    stripped_text = stripped_text[end+1:len(stripped_text)]
    leftover_wo_spaces = stripped_text.replace(' ','')
    
    if len(leftover_wo_spaces) > 1:
        find_breakpoint(split_length)

def find_breakpoint(split_length):
    global chunks
    global stripped_text
    global break_markers
    global chunks_ready

    if split_length == "short":
        split_min = 70
        split_max = 100
    elif split_length == "medium":
        split_min = 120
        split_max = 220
    else:
        # long
        split_min = 180
        split_max = 300

    #print(len(stripped_text))
    if len(stripped_text) > split_max:
        #print("--- in > " + str(split_max))
        step1 = 0
        step2 = 0
        step3 = 0
        step4 = 0
        
        for char_index in range(split_min,split_max):
            #print("1------- char index: " + str(char_index) + "length: " + str(len(stripped_text)))
            if stripped_text[char_index] in break_markers['step1']:
                # Save chunk and remove chunk from text
                step1 = 1
                #print("Create chunk 1")
                create_chunk(char_index,split_length)
                return True
                
        # If step1 faled
        if step1 == 0:
            for char_index in range(split_min,20,-1):
                #print("2------- char index: " + str(char_index) + "length: " + str(len(stripped_text)))
                if stripped_text[char_index] in break_markers['step2']:
                    # Save chunk and remove chunk from text
                    step2 = 1
                    #print("Create chunk 2")
                    create_chunk(char_index,split_length)
                    return True
                    
        # If step2 faled
        if step2 == 0:
            for char_index in range(split_max,20,-1):
                #print("3------- char index: " + str(char_index) + "length: " + str(len(stripped_text)))
                if stripped_text[char_index] in break_markers['step3']:
                    # Save chunk and remove chunk from text
                    step3 = 1
                    #print("Create chunk 3")
                    create_chunk(char_index,split_length)
                    return True

        # If step3 faled                
        if step3 == 0:
            for char_index in range(split_max,len(stripped_text)):
                #print("4------- char index: " + str(char_index) + "length: " + str(len(stripped_text)))
                if stripped_text[char_index] in break_markers['step4']:
                    # Save chunk and remove chunk from text
                    step4 = 1
                    #print("Create chunk 4")
                    create_chunk(char_index,split_length)
                    return True

        #print("strep4: " + str(step4))
        # If step3 faled
        if step4 == 0:
            #print("Create chunk 5")
            create_chunk(len(stripped_text),split_length)
            return True
    else:
        #print("--- in else")
        #print("----^^^^^-----Chunk list length: " + str(len(chunks)))
        chunks.append(stripped_text)
        #print("----^^^^^-----Chunk list after: " + str(len(chunks)))
        chunks_ready = True
        #for chunk in range(0,len(chunks)):
        #    print(f"{chunks[chunk]}\n")
        return True

if __name__ == "__main__":
    import os
    import unittest

    class Test(unittest.TestCase):
        def test_split_and_recombine_text(self):
            text = """
            This is a sample sentence.
            This is another sample sentence.
            This is a longer sample sentence that should force a split inthemiddlebutinotinthislongword.
            "Don't split my quote... please"
            """
            self.assertEqual(
                split_and_recombine_text(text, desired_length=20, max_length=40),
                [
                    "This is a sample sentence.",
                    "This is another sample sentence.",
                    "This is a longer sample sentence that",
                    "should force a split",
                    "inthemiddlebutinotinthislongword.",
                    '"Don\'t split my quote... please"',
                ],
            )

        def test_split_and_recombine_text_2(self):
            text = """
            When you are really angry sometimes you use consecutive exclamation marks!!!!!! Is this a good thing to do?!?!?!
            I don't know but we should handle this situation..........................
            """
            self.assertEqual(
                split_and_recombine_text(text, desired_length=30, max_length=50),
                [
                    "When you are really angry sometimes you use",
                    "consecutive exclamation marks!!!!!!",
                    "Is this a good thing to do?!?!?!",
                    "I don't know but we should handle this situation.",
                ],
            )

        def test_split_and_recombine_text_3(self):
            text_src = os.path.join(
                os.path.dirname(__file__), "../data/riding_hood.txt"
            )
            with open(text_src, "r") as f:
                text = f.read()
            self.assertEqual(
                split_and_recombine_text(text),
                [
                    "Once upon a time there lived in a certain village a little country girl, the prettiest creature who was ever seen. Her mother was excessively fond of her; and her grandmother doted on her still more. This good woman had a little red riding hood made for her.",
                    'It suited the girl so extremely well that everybody called her Little Red Riding Hood. One day her mother, having made some cakes, said to her, "Go, my dear, and see how your grandmother is doing, for I hear she has been very ill. Take her a cake, and this little pot of butter."',
                    "Little Red Riding Hood set out immediately to go to her grandmother, who lived in another village. As she was going through the wood, she met with a wolf, who had a very great mind to eat her up, but he dared not, because of some woodcutters working nearby in the forest.",
                    'He asked her where she was going. The poor child, who did not know that it was dangerous to stay and talk to a wolf, said to him, "I am going to see my grandmother and carry her a cake and a little pot of butter from my mother." "Does she live far off?" said the wolf "Oh I say,"',
                    'answered Little Red Riding Hood; "it is beyond that mill you see there, at the first house in the village." "Well," said the wolf, "and I\'ll go and see her too. I\'ll go this way and go you that, and we shall see who will be there first."',
                    "The wolf ran as fast as he could, taking the shortest path, and the little girl took a roundabout way, entertaining herself by gathering nuts, running after butterflies, and gathering bouquets of little flowers.",
                    'It was not long before the wolf arrived at the old woman\'s house. He knocked at the door: tap, tap. "Who\'s there?" "Your grandchild, Little Red Riding Hood," replied the wolf, counterfeiting her voice; "who has brought you a cake and a little pot of butter sent you by mother."',
                    'The good grandmother, who was in bed, because she was somewhat ill, cried out, "Pull the bobbin, and the latch will go up."',
                    "The wolf pulled the bobbin, and the door opened, and then he immediately fell upon the good woman and ate her up in a moment, for it been more than three days since he had eaten.",
                    "He then shut the door and got into the grandmother's bed, expecting Little Red Riding Hood, who came some time afterwards and knocked at the door: tap, tap. \"Who's there?\"",
                    'Little Red Riding Hood, hearing the big voice of the wolf, was at first afraid; but believing her grandmother had a cold and was hoarse, answered, "It is your grandchild Little Red Riding Hood, who has brought you a cake and a little pot of butter mother sends you."',
                    'The wolf cried out to her, softening his voice as much as he could, "Pull the bobbin, and the latch will go up." Little Red Riding Hood pulled the bobbin, and the door opened.',
                    'The wolf, seeing her come in, said to her, hiding himself under the bedclothes, "Put the cake and the little pot of butter upon the stool, and come get into bed with me." Little Red Riding Hood took off her clothes and got into bed.',
                    'She was greatly amazed to see how her grandmother looked in her nightclothes, and said to her, "Grandmother, what big arms you have!" "All the better to hug you with, my dear." "Grandmother, what big legs you have!" "All the better to run with, my child." "Grandmother, what big ears you have!"',
                    '"All the better to hear with, my child." "Grandmother, what big eyes you have!" "All the better to see with, my child." "Grandmother, what big teeth you have got!" "All the better to eat you up with." And, saying these words, this wicked wolf fell upon Little Red Riding Hood, and ate her all up.',
                ],
            )

    unittest.main()
