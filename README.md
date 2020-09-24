# pak-extractor
This simple python script will extract data from game ```.pak``` files, such as Arcturus.

The script sometimes need a time to extract all files (it depends for the size of the .pak). 
Because of that, the script won't restract the extracted files, unless you run the command line "forced" (i.e. ```python3 read_pak.py forced```).

The first time you run this script, you need to setup the variables ```folder_script``` ( the folder script :) ) and ```name_extrated``` (the name of .pak file). The ```extensions``` variable is pettry straightfoward, since you denote all extensions you want to be extracted. Then, when you run, it will create a json file <the same .pak name>_info.json (i.e. ```data.pak``` => ```data_info.json```)
This file will contaning all information about the files and folders included in .pak, such as: file name; size file name; original size; a flag, representing if is folder or file, and so on
After that, the script will create two files: <the same .pak name>_all_files.txt and <the same .pak name>_all_directories.txt (i.e. ```data.pak``` => ```data_all_files.txt``` & ```data_all_directories.txt```), that will containing all names of directories and files found in .pak. (This file isn't important here, it works like a "preview" of what will be extracted).

Now, the script will extract all data from .pak. It is important to note, python is slow in some cases to extract all the whole data, since it is an interpreted language. For this case, i've implemented the same decode algorithm in C, and this can be called when the python script extracts the files. 

If you do, you need to compile the file ```decoder.c``` with your favorite compiler, and put the program generated in the same folder of the python script. Also, you need to denote the file name in the variable decoder_name, on the top of python script. (i.e. ```decoder.exe```). If you want to force all files be extracted with C decoder, you should type 'fast' in command line (i.e. ```python3 read_pak.py fast```). But it isn't recommended, since the overhead to call a new process to extract all the files (OS stuff... We can't control it...). For this sake, i trunk a value of 140.000 bytes (~136kb) to permute the decoder, between python and the C one. I tested this, and achieve good performance over an intel i7-4790 processor (~35 minutes from hybrid extract vs > 24h from pure python; to extract all data.pak from arcturus).

That's all, folks :)
