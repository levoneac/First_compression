# First_compression
My first time trying to create a text compressor
This was a little project i did during the christmas holidays of 2023, after watching [computerphiles videos on huffman encoding and lz77](https://www.youtube.com/watch?v=umTbivyJoiI)

Its very slow(partly thanks to it being in python), but i wanted to do it without any help other than the videos. The files also need to be quite big for it to be of any use (around 1MB).

An example textfile of 1141KB got compressed into 751KB - A 34% decrease, the caveat being, it took 10 minutes :D

## How to use it:
  ### Encoding:
    `python First_compressor.py -e file.txt -w file_to_write_result_to.txt`

  ### Decoding:
    `python First_compressor.py -d encoded_file.txt -w file_to_write_result_to.txt`

  If `-w` isnt given, it will print the result to the terminal.
  You can also supply the input for -e/--encode and -d/--decode with a string enclodes in quotes.
