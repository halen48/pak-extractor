import re
import json
import os
import sys

codec_binary = 'latin-1'

header = bytes([0x04,0x02,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00]).decode(encoding=codec_binary)
'''
bmp file header:
2 bytes = 'BM'
4 bytes = 'Size'
4 bytes = 4x'0x0'
'''
#===============================================================================
folder_script = 'S:\Off-Games\Arcturus\\'
decoder_name = "decoder.exe"
name_extracted = 'data'
#extentions that will be extracted
extensions = ['spr','act','rsw','gnd','gat']
ext_extract = {}
for extension in extensions:
    ext_extract[extension] = re.compile(r'data/[^\.\0]+\.'+extension)
#===============================================================================

print('Reading')
with open(folder_script+name_extracted+".pak",'rb') as f:
    characters = f.read().decode(encoding=codec_binary)
content = characters.split(header)
#spr_count_content = content[0].count(spr_header)
text = content[1]
chunks = content[0]
#===============================================================================
try:
    with open(folder_script+name_extracted+"_infos.json", encoding=codec_binary) as f:
        infos = json.load(f)
    all_files =[]
    all_directories =[]
    for name in infos:
        if(infos[name]['flag'] == 1):
            all_files.append(name)
        else:
            all_directories.append(name)
except FileNotFoundError:
    #the files/folders have the header as: name followed by \0
    regex_file_s = re.compile(r'(data/[^\0]+)\0')
    all_files = regex_file_s.findall(text)
    infos = {}
    pointer = 0
    for entry in all_files:
        offset = text.find(entry+chr(0x00))
        index_after = offset+len(entry)+1
        index_before = offset-14
        #0
        tamanho_nome = text[index_before]
        #1
        flag = text[index_before+1]
        #2~5
        start = text[index_before+2:index_before+6]
        #6~9
        size = text[index_before+6:index_before+10]
        #10~14
        original_size = text[index_before+10:index_before+14]
        #'size':int.from_bytes(tamanho[::-1].encode(),byteorder='big')
        infos[entry] = {'size_name':int.from_bytes(tamanho_nome.encode(encoding=codec_binary),byteorder='big'),
        'flag':int.from_bytes(flag.encode(encoding=codec_binary),byteorder='big'),
        'original size':int.from_bytes(original_size[::-1].encode(encoding=codec_binary),byteorder='big'),
        'start': int.from_bytes(start[::-1].encode(encoding=codec_binary),byteorder='big')} #the next 8 bits stores the information
        infos[entry]['size'] = max(0,int.from_bytes(size[::-1].encode(encoding=codec_binary),byteorder='big'))
        infos[entry]['end'] = infos[entry]['size']+infos[entry]['start']
        infos[entry]['chunk'] = [hex(ord(c)) for c in text[index_before:offset]]+[entry]
        pointer = infos[entry]['end']

    with open(folder_script+name_extracted+"_infos.json", 'w+',encoding=codec_binary) as f:
        json.dump(infos,f, ensure_ascii=False, indent=3)

    all_directories = {}
    for entry in all_files:
        path = entry.split('/')
        if(path[-1].find('.')):
            paths = '/'.join(path[:-1])
            if(not paths in all_directories):
                all_directories[paths] = 1
            else:
                all_directories[paths] += 1

    with open(folder_script+name_extracted+"_all_files.txt",'w+',encoding=codec_binary) as f:
        for entry in all_files:
            if(entry[-4] == '.'):
                f.write(entry+'\n')

    with open(folder_script+name_extracted+"_all_directories.txt",'w+',encoding=codec_binary) as f:
        for path in all_directories:
            f.write(str(path+':'+str(all_directories[path]))+'\n')
#===============================================================================
folder_extract = folder_script+'extracted/'
for path in all_directories:
    print('Creating',folder_extract+path,end='\r')
    try:
        os.mkdir(folder_extract+path)
    except FileExistsError:
        print(folder_extract+path,'already extracted, skipping...',end='\r')
    #print()
#===============================================================================================
def decode_file(file_convert,size_file,content):

    content_index_read = [0]
    full_index_read = 0

    def get_next_byte_file(content, i = content_index_read,qt=1):
        index = 0
        ret = ''
        while(index < qt):
            try:
                ret += chr(content[i[0]])
                i[0]+=1 
                index+=1  
            except IndexError:
                print()
                print(file_convert)
                print("erro!")
                return None

        return bytes(str(ret),'latin-1')

    #infos[file_convert]['original size']
    print('%s : file size: (%d/%d)'%(file_convert,len(content),size_file))
    final_file = bytes()
    i = 0
    mask = content[0]&0xFF
    content = content[1:]
    masks_history = []
    
    while (content_index_read[0] < len(content)):
        
        print('Converting %.2f%%'%(100*content_index_read[0]/len(content)),end='\r')
        while(i < 8):
            if(mask&1):            
                try:
                    mask2 = get_next_byte_file(content,qt=2)
                    masks_history.append((hex(mask2[0]),hex(mask2[1])))
                    shifting = (mask2[1]>>4)+2
                    index_offset = ((mask2[1]&0xf)<<8)+mask2[0]
                    final_file += get_next_byte_file(final_file,i=[full_index_read-index_offset],qt=shifting)
                except:
                    return
            else:
                final_file += get_next_byte_file(content)
            full_index_read = len(final_file)
            i+=1
            mask >>= 1
            if(content_index_read[0] >= len(content) ):
                break
        if(content_index_read[0] < len(content) ):
            i = 0
            mask = int.from_bytes(get_next_byte_file(content), "big")

    #final_file = final_file[0:original_size] #trim
    with open(file_convert,'wb') as f:
        f.write(final_file)
#===============================================================================================
#converting to numbers
for file_ in all_files:
    buffer = ''
    if(infos[file_]['size']): # and file_.find('/sprite/') != -1
        if(not 'forced' in sys.argv):
            try:
                open(folder_extract+file_).close()
                print('Skipping to file %20s Offset: %09d    '%(str(folder_extract+file_)[10:],infos[file_]['end']),end='\r')
                continue
            except FileNotFoundError:
                pass
        print('Creating %20s Offset: %09d    '%(str(folder_extract+file_)[10:],infos[file_]['end']),end='\r')
        if('fast' in sys.argv or infos[file_]['original size'] > 140000): #100kb
            with open(folder_extract+file_,'wb+') as f:
                f.write(chunks[infos[file_]['start']:min(len(chunks),infos[file_]['end'])].encode(encoding=codec_binary))
            os.system(folder_script+'%s "'%(decoder_name)+
            folder_extract+file_+'" '+
            str(infos[file_]['size'])+' '+
            str(infos[file_]['original size']))
        else:
            decode_file(folder_extract+file_,infos[file_]['original size'],chunks[infos[file_]['start']:min(len(chunks),infos[file_]['end'])].encode(encoding=codec_binary))
        print('%d bytes writed in %s'%(infos[file_]['original size'],folder_extract+file_)) 
        

#===============================================================================
for extension in ext_extract:
    print('Writing %s_files.txt'%extension)
    with open(folder_script+name_extracted+"_"+extension+"_files.txt",'w+',encoding=codec_binary) as f:
        for files in ext_extract[extension].findall(text):
            f.write(files+'\n')

print('End :)')