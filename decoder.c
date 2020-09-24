#include <stdio.h>
#include <stdlib.h>

typedef unsigned long long uint64;
typedef unsigned char uint8;
typedef short unsigned int uint16;

uint64 get_next_byte_file(uint8* content, uint64 i, int qt, uint8* ret) {
	int index = 0;

	while (index < qt)
		ret[index++] = content[i++];
	return i;
}

/*
argv[1] = Nome do arquivo
argv[2] = Conteudo do arquivo
argv[3] = Tamanho do arquivo
argv[4] = Tamanho Original
*/
#define name_file argv[1]
#define content_size_char argv[2]
#define original_size_char argv[3]
int main(const int argc, const char* argv[]) {

	uint64 content_size = atoll(content_size_char);
	uint64 original_size = atoll(original_size_char);
	uint8 * content = malloc(sizeof(uint8) * content_size);
	
	FILE* unpacked;
	unpacked = fopen(name_file, "rb");
	fread(content, content_size, 1, unpacked);
	fclose(unpacked);
	
	printf("%s : file size (%llu/%llu)\n", name_file, content_size, original_size);

	uint8 mask;
	uint8 * final_file = malloc(sizeof(uint8)*original_size);
	memset(final_file, 0x69, original_size);
	
	uint64 full_index_read = 0, content_index_read = 0;
	
	uint64 i;
	uint8 deslocamento;
	uint16 index_offset;
	uint8 * buffer;
	#define mask2 buffer
	while (content_index_read < content_size) {
		mask = content[content_index_read++];
		i = 0;
		for (i = 0; i < 8 && content_index_read < content_size; i++) {
			if (mask & 1) {

				mask2 = malloc(sizeof(uint8)*2);
				content_index_read = get_next_byte_file(content, content_index_read, 2, buffer);
				deslocamento = (mask2[1] >> 4) + 2;
				index_offset = ((mask2[1] & 0xf) << 8) + mask2[0];
				free(mask2);
				buffer = malloc(sizeof(uint8) * deslocamento);
				get_next_byte_file(final_file, full_index_read - index_offset, deslocamento, buffer);
				memcpy(final_file + full_index_read, buffer, sizeof(uint8)*deslocamento);
				free(buffer);

				full_index_read += deslocamento;
			} else {
				final_file[full_index_read++] = content[content_index_read++];
			}
			mask >>= 1;
		}
		printf("Converting %.2f%%\r", 100.*content_index_read / content_size);
	}

	FILE* file;
	file = fopen(name_file, "wb+");
	fwrite(final_file, 1, sizeof(uint8)*original_size, file);
	fclose(file);

	return 0;
}
