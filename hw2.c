#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/wait.h>
#include <sys/types.h>
#include <ctype.h>
#include <string.h>
#include <sys/shm.h>

static const int X[8] = {-2, -1, 1, 2, 2, 1, -1, -2};
static const int Y[8] = {-1, -2, -2, -1, 1, 2, 2, 1};

// if flag == 1, then use waitpid function, else not
// gcc -D <variable> means defining it while compiling
#ifdef NO_PARALLEL
static const int flag = 1;
#else
static const int flag = 0;
#endif

int max(int a, int b){
	return a > b ? a : b;
}

// judge the position is valid
int isValid(int x, int y, int m, int n){
	if (x >= 0 && x < m && y >= 0 && y < n)
		return 1;
	else
		return 0;
}

// judge a position is visited
int isVisited(int *visit, int index, int size){
	int i = 0;
	for (i = 0; i < size; i++){
		if (*(visit + i) == index){
			return 1;
		}
	}
	return 0;
}

// dfs method, the core function
// return [a, b]
// a means the farthest moving distance at least 1
// b means how many times it successfully covers all the grids 
void dfs(int m, int n, int* visited, int size, int shmid){
	
	int pid = getpid();
	if (size == m * n){
		printf("PID %d: Sonny found a full knight's tour; notifying top-level parent\n", pid);
		int *result = (int *)shmat(shmid, NULL, 0);
		*result = m * n;
		*(result + 1) += 1;
		shmdt(result);
		return;
	}
	
	int x = *(visited + size - 1) / n;
	int y = *(visited + size - 1) % n;
	int count_continue = 0, i = 0, tempX, tempY;
	//int* choices = calloc(8, sizeof(int));
	int choices[8];
	
	for (i = 0; i < 8; i++) {
		tempX = x + *(X + i);
		tempY = y + *(Y + i);
		if (isValid(tempX, tempY, m, n)){
			if (!isVisited(visited, tempX * n + tempY, size)){
				*(choices + count_continue) = tempX * n + tempY;
				count_continue++;
			}
		}
	}
	
	if (count_continue == 0){
		int *result = (int *)shmat(shmid, NULL, 0);
		*result = max(*result, size);
		printf("PID %d: Dead end at move #%d\n", pid, size);
		shmdt(result);
	}
	
	else if (count_continue == 1){
		int index = *choices;
		*(visited + size) = index;
		dfs(m, n, visited, size + 1, shmid);
		int* result = (int *)shmat(shmid, NULL, 0);
		*result = max(*result, size);
		shmdt(result);
	}
	
	else{
		printf("PID %d: %d possible moves after move #%d; creating %d child processes...\n", pid, count_continue, size, count_continue);
		for (i = 0; i < count_continue; i++){
			int tpid = fork();
			
			if (tpid < 0){
				perror("Fork failed.\n");
			}
			
			else if (tpid == 0){ // child process
				int index = *(choices + i);
				*(visited + size) = index;
				dfs(m, n, visited, size + 1, shmid);
				int* result = (int *)shmat(shmid, NULL, 0);
				*result = max(*result, size);
				shmdt(result);
				//free(choices);
				//free(visited);
				exit(0);
				//exit(100 * (*(result + 1)) + (*result)); // 100 * times + distance since distance <= m * n
			}
			
			else{ // parent process
				int stat_val;
				if (flag == 1 || flag == 0){
					waitpid(tpid, &stat_val, 0);
//					int status = WEXITSTATUS(stat_val);
//					int distance = status % 100;
//					int times = status / 100;
//					*result = max(*result, distance);
//					*(result + 1) += times;
				}
				else{
					;
				}
			}
			
		}
	}
	
	//free(choices);
	return;
}

int main(int argc, char** argv){
	
	setvbuf( stdout, NULL, _IONBF, 0 );
	
	// for example, $bash ./a.out 3 3 0 0 means argc = 5
	if (argc != 5){
		fprintf(stderr, "ERROR: Invalid argument(s)\nUSAGE: hw2.out <m> <n> <r> <c>\n");
		return EXIT_FAILURE;
	}
	
	int i = 1;
	for (i = 1; i < 3; i++){
		char* temp = *(argv + i);
		if (atoi(temp) < 3){
			fprintf(stderr, "ERROR: Invalid argument(s)\nUSAGE: hw2.out <m> <n> <r> <c>\n");
			return EXIT_FAILURE;
		}
	}
	
	for (i = 3; i < 5; i++){
		char* temp = *(argv + i);
		int length = atoi(*(argv + i - 2));
		if (atoi(temp) >= length){
			fprintf(stderr, "ERROR: Invalid argument(s)\nUSAGE: hw2.out <m> <n> <r> <c>\n");
			return EXIT_FAILURE;
		}
		if (atoi(temp) < 0){
			fprintf(stderr, "ERROR: Invalid argument(s)\nUSAGE: hw2.out <m> <n> <r> <c>\n");
			return EXIT_FAILURE;
		}
		if (atoi(temp) == 0){
			if (strlen(temp) > 1 || !isdigit(*temp)){
				fprintf(stderr, "ERROR: Invalid argument(s)\nUSAGE: hw2.out <m> <n> <r> <c>\n");
				return EXIT_FAILURE;
			}
		}
	}
	
	int filedes[2];
	pipe( filedes );
	
	int *attempt = calloc(1, sizeof(int));
	free(attempt);
	
	int shmid;
	shmid = shmget(IPC_PRIVATE, 1000, IPC_CREAT | 0600);
	
	int m = atoi(*(argv + 1));
	int n = atoi(*(argv + 2));
	int x = atoi(*(argv + 3));
	int y = atoi(*(argv + 4));
	int visited[m * n];
	*visited = x * n + y;
	int size = 1, pid = getpid();
	
	printf("PID %d: Solving Sonny's knight's tour problem for a %dx%d board\n", pid, m, n);
	printf("PID %d: Sonny starts at row %d and column %d (move #1)\n", pid, x, y);
	dfs(m, n, visited, size, shmid);
	int *result;
	result = (int *)shmat(shmid, NULL, 0);
	if (*(result + 1)){
		printf("PID %d: Search complete; found %d possible paths to achieving a full knight's tour\n", pid, *(result + 1));
	}
	else{
		printf("PID %d: Search complete; best solution(s) visited %d squares out of %d\n", pid, *result, m * n);
	}
	//free(visited);
	
	// https://blog.csdn.net/mayifan_blog/article/details/100054113  
	shmdt(result);
	shmctl(shmid, IPC_RMID, NULL); // delete the shared memory
	
	return EXIT_SUCCESS;
}

