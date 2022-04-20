#include <stdio.h>
#include <stdlib.h>
#include <ctype.h>
#include <string.h>

int find(int num, char* list)
{
    setvbuf( stdout, NULL, _IONBF, 0 );
    char* temp = calloc(12, sizeof(char));
    sprintf(temp, "%d", num);
    
    char *ret;
    ret = strstr(list, temp);
    
    if (ret)
    {
    	free(temp);
        return 1;
    }
    else
    {
    	free(temp);
    	return 0;
    }
}

int main(int argc, char** argv)
{
    
	// for example, "$bash ./a.out 1 2" with argc == 3
	if (argc < 3)
	{
		fprintf(stderr, "ERROR: <There should be three argumnents.>\n");
		return EXIT_FAILURE;
	}
	
	int cache_size = atoi(*(argv + 1));
	if (cache_size <= 0) // maybe we need to add "*(argv + 1) != NULL"
	{
	    fprintf(stderr, "ERROR: <Cache size is not valid.>\n");
	    return EXIT_FAILURE;
	}
	
	int k = 2;
	char** cache = calloc(cache_size, sizeof(char*));
	char *buffer = calloc(12, sizeof(char));
	int ptr = 0, index = 0, num = 0, length = 0, t = 0, flag = 0;
	char temp;
	for (k = 2; k < argc; k++)
	{
		FILE *fp;
		fp = fopen(*(argv + k), "r");
		if (fp == NULL)
		{
			fprintf(stderr, "ERROR: <File does not exist.>\n");
			return EXIT_FAILURE;
		}
		
		while (fp)
		{
			if (feof(fp))
			{
				break;
			}
			
			temp = fgetc(fp);
			
			if (isdigit(temp))
			{
			    *(buffer + ptr) = temp;
			    ptr++;
			    num = num * 10;
			    t = temp - '0';
			    num = num + t;
			    flag = 1;
			}
			else
			{
			    if (flag == 1)
			    {
			    	*(buffer + ptr) = '\0';
			    	index = num % cache_size;
			    	
			    	// calloc
			    	if (*(cache + index) == 0)
			    	{
			    		printf("Read %d ==> cache index %d (calloc)\n", num, index);
			    		char *new_list = calloc(12, sizeof(char));
			    		strcpy(new_list, buffer);
			    		*(cache + index) = new_list;
			    	}
			    	
			    	// realloc
			    	else
			    	{
			    		if (find(num, *(cache + index)) == 1)
			    		{
			    			printf("Read %d ==> cache index %d (skipped)\n", num, index);
			    		}
			    		
			    		else
			    		{
			    			printf("Read %d ==> cache index %d (realloc)\n", num, index);
			    			length = strlen(*(cache + index));
			    			*(cache + index) = (char*) realloc(*(cache + index), 12 + 2 + length);
			    			strcat(*(cache + index), ", ");
			    			strcat(*(cache + index), buffer);
			    		}
			    	}
			    	
			    	ptr = 0;
			    	num = 0;
			    	length = 0;
			    	flag = 0;
			    	memset(buffer, 0, 12);
			    }
			    
			}
			
		}
		fclose(fp);
	}
	
	
	
	free(buffer);
	printf("========================================\n");
	
	int i = 0;
	for (i = 0; i < cache_size; i++)
	{
		if (*(cache + i) == NULL)
		{
			continue;
		}
		
		else
		{
			printf("Cache index %d ==> %s\n", i, *(cache + i));
			free(*(cache + i));
		}
	}
	
	free(cache);
	
	return EXIT_SUCCESS;
}
