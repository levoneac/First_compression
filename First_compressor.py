import argparse
from pathlib import Path
import ast


encoding_bits = 19

class compressor:
    def __init__(self, data, n=6) -> None:
        self.data = data
        self.seen = dict()
        self.pointer = 0
        self.compressed = ""
        self.n = n
        self.binary = ""
        self.encoded = ""
        self.format = ""
        

    def yield_word(self, text:str) -> str:
        text = text.split(sep=" ")
        while len(text) > 0:
            yield text[0]
            text = text[1:]
    
    def compress(self):
        for word in self.yield_word(self.data):
            if len(word) > self.n:

                if word in self.seen.keys():
                    self.compressed += (str(self.seen[word]) + " ")
                    self.pointer += (len(word)+1)
                    
                else:
                    #DEBUG
                    #print(f"pointer {self.pointer}, real: {self.data.find(word)}")
                    #print(f"word: {self.data[self.pointer:(self.pointer + len(word))]}, real: {word}")
                    
                    self.seen[word] = f"¤{self.pointer},{len(word)-1}¤"
                    self.compressed += (word + " ")
                    
                    self.pointer += (len(word)+1)
            else:
                self.compressed += (word + " ")
                self.pointer += (len(word)+1)
        return self.compressed

    def huffman(self):
        total = 0
        total_words = 0
        huff_dict = dict()
        #count instances of word
        for word in self.yield_word(self.compressed):
            if "¤" in word:
                total+=1
                if word in huff_dict:
                    huff_dict[word] = huff_dict[word]+1
                else:
                    huff_dict[word] = 1
            else:
                for letter in word:
                    total+=1   
                    if letter in huff_dict:
                        huff_dict[letter] = huff_dict[letter]+1
                    else:
                        huff_dict[letter] = 1
            total_words+=1
        #spaces
        huff_dict[" "] = total_words-2                
        
        huff_dict_sorted = sorted(huff_dict.items(), key= lambda x: x[1])
    

        #tree structure 
        class NodeAmountError(Exception):
            def __init__(self, *args: object) -> None:
                super().__init__(*args)
        #make tree structure
        class Leaf:
            def __init__(self, letter, amount) -> None:
                self.leaf_value = letter
                self.amount = amount
        class Node:
            def __init__(self, r_amount = None, l_amount = None, r_letter = None, l_letter=None) -> None:
                if r_letter is not None and not (isinstance(r_letter, (Node, Leaf))):
                    if r_amount is None:
                        raise NodeAmountError
                    self.right_node = Leaf(r_letter, r_amount)
                else:
                    self.right_node = r_letter
                if l_letter is not None and not (isinstance(l_letter, (Node, Leaf))):
                    if l_amount is None:
                        raise NodeAmountError
                    self.left_node = Leaf(l_letter, l_amount)
                else:
                    self.left_node = l_letter

                self.amount = self.left_node.amount + self.right_node.amount

        while len(huff_dict_sorted) > 1:
            points = huff_dict_sorted[0:2]
            #0 = left, 1 = right
            huff_dict_sorted = huff_dict_sorted[2:]

            node = Node(r_letter=points[1][0], r_amount=points[1][1], l_letter=points[0][0], l_amount=points[0][1])

            huff_dict_sorted.append((node, node.amount))
            huff_dict_sorted = sorted(huff_dict_sorted, key= lambda x: x[1])


        #assign binary values to letters
        self.huff_tree = huff_dict_sorted[0][0]
        
        huff_binaries = dict()
        sequence = ""
        def assign_values(self, binary_sequence, node):
            if isinstance(node, Leaf):
                huff_binaries[node.leaf_value] = binary_sequence
                binary_sequence = binary_sequence[:-1]
                return 0
            
            #left
            assign_values(self, binary_sequence+"0", node.left_node)

            #right
            assign_values(self,binary_sequence+"1", node.right_node)
            return 0
        
        assign_values(self, sequence, self.huff_tree)


        #encode
        self.binary = ""
        for word in self.yield_word(self.compressed):
            if word.startswith("¤") or word[::-1].startswith("¤"):
                self.binary += (huff_binaries[word] + huff_binaries[" "])
            else:
                for letter in word:
                    self.binary += (huff_binaries[letter])
                self.binary += huff_binaries[" "]
        
        """
        #RLE the bits
        if (self.binary[0] != "0") and (self.format == ""):
            self.format += "0"
            print(self.binary[0])
            print("added 0")
        
        
        n = 0
        while n < len(self.binary):
            bit = self.binary[n]
            number_of_same = 0

            try:
                while bit == self.binary[n + number_of_same]:
                    #print(self.binary[n: n+number_of_same])
                    number_of_same += 1
            except IndexError: #qucikfix for now lol
                pass
            if number_of_same > 10:
                self.format += f"{number_of_same//10}.{number_of_same%10}"

            self.format += f"{number_of_same}"
            n = n + number_of_same
       
        return str(self.format) + ";" + str(huff_binaries)
        """

        
        while len(self.binary) >= encoding_bits:
            #adding one to the start of the binary sequence so that the leading zeros dont get ignored
            self.encoded += chr(int("1" + self.binary[:encoding_bits], 2))
            
            #print(f"{self.binary[:encoding_bits]}, {chr(int(self.binary[:encoding_bits], 2))}, {format(ord(chr(int(self.binary[:encoding_bits], 2))), 'b')}")
            self.binary = self.binary[encoding_bits:]
        
        #print(f"last: {self.binary}")
        self.encoded += chr(int("1" + self.binary, 2))
        #print(f"encoded: {self.encoded}")
        return self.encoded + "HUFFMAN" + str(huff_binaries)
        


class decompressor:
    def __init__(self, data) -> None:
        self.data = data
        self.decompressed = ""
        self.dehuffed = ""

    def yield_word(self, text:str) -> str:
        text = text.split(sep=" ")
        while len(text) > 0:
            yield text[0]
            text = text[1:]

    def dehuff(self):
        encoded, key = self.data.split(sep="HUFFMAN")

        
        encoded_binary = ""
        for letter in encoded:
            pre = format(ord(letter), "b")[1:]
            encoded_binary += pre
        

        #switch key and value
        key = dict((v,k) for k,v in ast.literal_eval(key).items())


        r = 0
        l = 0
        while r < len(encoded_binary):
            if encoded_binary[l:r] in key:
                self.dehuffed += key[encoded_binary[l:r]]
                l = r
            r+=1
        return self.dehuffed
        

    def decompress(self, input_is_huffman=True):
        if input_is_huffman == True:
            self.data = self.dehuff()

        for word in self.yield_word(self.data):
            #print(word)
            if word.startswith("¤") and word[::-1].startswith("¤"):
                index = word.strip("¤¤").split(",")
                self.decompressed += (self.decompressed[int(index[0]):(int(index[0])+int(index[1])+1)] + " ")
            
            else:
                self.decompressed += (word + " ")
        
        self.decompressed = self.decompressed.rstrip()

        return self.decompressed
        



if __name__  == "__main__":
    script_dir = Path(__file__).parent
    
    parse = argparse.ArgumentParser(description="Huffman+LZ ncoder")
    group = parse.add_mutually_exclusive_group()
    group.add_argument("-e", "--encode", type=str, nargs="*", default=" ", metavar="string_to_encode or file")
    group.add_argument("-d", "--decode", type=str, default=" ", metavar="string_to_decode or file", nargs="*")
    #parse.add_argument("-s", "--stats", action="store_true")
    parse.add_argument("-w", "--write-to-file", default=" ", metavar="FILE", type=str)
    
    arg = parse.parse_args()

    #print(arg)
    if arg.encode[0] != " " and len(arg.encode) == 1:
        data = arg.encode[0]
        if len(data.split(sep=" ")) == 1:
            with open(f"{script_dir/data}", mode="r", encoding="utf-8") as f:
                data = f.read()
        length = len(data)

        cmp = compressor(data)
        cmp.compress()
        ret = cmp.huffman()
        
    
    elif arg.decode[0] != " " and len(arg.decode) == 1:
        data = arg.decode[0]
        if len(data.split(sep=" ")) == 1:
            with open(f"{script_dir/data}", mode="r", encoding="utf-8") as f:
                data = f.read()

        length = len(data)

        dcmp = decompressor(data)
        dcmp.decompress()
        ret = dcmp.decompressed
        

    else:
        print("Specify encoding or decoding, or maybe you forgot qoutemarks?")
        exit()
    
    if arg.write_to_file != " ":
        with open(f"{script_dir/arg.write_to_file}",mode="w", encoding="utf-8") as f:
            f.write(ret)
    
    else:
        print(ret)

    
    

        
        
       




