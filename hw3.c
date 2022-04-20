#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <pthread.h>
#include <string.h>
#include <ctype.h>


// 全局变量区
static const int X[8] = {-2, -1, 1, 2, 2, 1, -1, -2};
static const int Y[8] = {-1, -2, -2, -1, 1, 2, 2, 1};

// 最大线程数，感觉应该不会太多，一万个就已经很炸裂了 
#define MAX_THREAD 100000
pthread_t threads[MAX_THREAD];


// gcc -D <variable> means defining it while compiling
#ifdef NO_PARALLEL
static const int flag = 1;
#else
static const int flag = 0;
#endif

extern int next_thread_id;        /* initialize to 1 */

extern int max_squares;           /* initialize to 0 */

extern int total_tours;           /* initialize to 0 */

struct Arg {
	int m, n, size, thread_id, father_id;
	int *visited;
};

//int max(int a, int b){
//	return a > b ? a : b;
//} 

// 判断位置是否合法 
int isValid(int x, int y, int m, int n){
	if (x >= 0 && x < m && y >= 0 && y < n)
		return 1;
	else
		return 0;
}

// 判断一个点是否被访问过 
int isVisited(int *visit, int index, int size){
	int i = 0;
	for (i = 0; i < size; i++){
		if (*(visit + i) == index){
			return 1;
		}
	}
	return 0;
}


// 检测参数合法性 
int judge_argument(int argc, char *argv[]) {
	
	if (argc != 5){
		fprintf(stderr, "ERROR: Invalid argument(s)\nUSAGE: a.out <m> <n> <r> <c>\n");
		return EXIT_FAILURE;
	}
	
	int i = 1;
	for (i = 1; i < 3; i++){
		char* temp = *(argv + i);
		if (atoi(temp) < 3){
			fprintf(stderr, "ERROR: Invalid argument(s)\nUSAGE: a.out <m> <n> <r> <c>\n");
			return EXIT_FAILURE;
		}
	}
	
	for (i = 3; i < 5; i++){
		char* temp = *(argv + i);
		int length = atoi(*(argv + i - 2));
		if (atoi(temp) >= length){
			fprintf(stderr, "ERROR: Invalid argument(s)\nUSAGE: a.out <m> <n> <r> <c>\n");
			return EXIT_FAILURE;
		}
		if (atoi(temp) < 0){
			fprintf(stderr, "ERROR: Invalid argument(s)\nUSAGE: a.out <m> <n> <r> <c>\n");
			return EXIT_FAILURE;
		}
		if (atoi(temp) == 0){
			if (strlen(temp) > 1 || !isdigit(*temp)){
				fprintf(stderr, "ERROR: Invalid argument(s)\nUSAGE: a.out <m> <n> <r> <c>\n");
				return EXIT_FAILURE;
			}
		}
	}
	
	return EXIT_SUCCESS;
}


// 复制一个一维数组 
//int* copy_list(int* list, int size) {
//	int result[size], i = 0;
//	int* r = result;
//    for (i = 0; i < size; i++) {
//    	result[i] = list[i];
//    }
//    return r;
//}

// int m, int n, int size, int thread_id, int father_id, int* visited
void* dfs(void* a) {
	
	struct Arg a_temp = *(struct Arg *)a;
	int m = a_temp.m, n = a_temp.n, size = a_temp.size, thread_id = a_temp.thread_id, father_id = a_temp.father_id;
	int *visited = a_temp.visited;
	
	if (size == m * n) {
		if (thread_id != 0) {
			printf("T%d: Sonny found a full knight's tour; incremented total_tours\n", thread_id);
		}
		else {
			printf("MAIN: Sonny found a full knight's tour; incremented total_tours\n");
		}
		total_tours++;
		max_squares = m * n;
		return NULL;
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
		if (size > max_squares) {
			if (thread_id != 0) {
				printf("T%d: Dead end at move #%d; updated max_squares\n", thread_id, size);
			}
			else {
				printf("MAIN: Dead end at move #%d; updated max_squares\n", size);
			}
			max_squares = size;
		}
		else {
			if (thread_id != 0) {
				printf("T%d: Dead end at move #%d\n", thread_id, size);
			}
			else {
				printf("MAIN: Dead end at move #%d\n", size);
			}
		}
	}
	
	else if (count_continue == 1) {
		int index = *choices;
		*(visited + size) = index;
		struct Arg arg = {m, n, size + 1, thread_id, father_id, visited};
		dfs((void *)&arg);
	}
	
	else { // else if (count_continue > 1)
		if (thread_id != 0) {
			printf("T%d: %d possible moves after move #%d; creating %d child threads...\n", thread_id, count_continue, size, count_continue);
		}
		else {
			printf("MAIN: %d possible moves after move #%d; creating %d child threads...\n", count_continue, size, count_continue);
		}
		
		int i = 0;
		for (i = 0; i < count_continue; i++) {
			//int* new_visited = copy_list(visited, m * n);
			int new_visited[m * n];
			int j = 0;
			for (j = 0; j < m * n; j++) {
				new_visited[j] = visited[j];
			}
			int index = *(choices + i);
			int current_tid = next_thread_id;
			
			*(new_visited + size) = index;
			struct Arg arg = {m, n, size + 1, current_tid, thread_id, new_visited};
			next_thread_id++;
			
			//dfs((void *)&arg);
			pthread_create(&threads[current_tid], NULL, dfs, (void *)&arg);
			if (flag == 1 || flag == 0) {
				pthread_join(threads[current_tid], NULL);
				if (thread_id == 0) {
					printf("MAIN: T%d joined\n", current_tid);
				}
				else {
					printf("T%d: T%d joined\n", thread_id, current_tid);
				}
				
			}
			
		}
		
	}
	
	return NULL;
}


int simulate(int argc, char *argv[]) {
	
	// 别忘了这个 
	setvbuf( stdout, NULL, _IONBF, 0 );
	
	// 判断参数合法性 
	int judge = judge_argument(argc, argv);
	if (judge == EXIT_FAILURE) {
		return EXIT_FAILURE;
	}
	
	// 测试用的 
	int *attempt = calloc(1, sizeof(int));
	free(attempt);
	
	//测试用的
	pthread_mutex_t f_lock;
	int try_temp = 0;
	if (try_temp) {
		pthread_mutex_lock(&f_lock);
	} 
	
	// 尺寸 坐标 
	int m = atoi(*(argv + 1));
	int n = atoi(*(argv + 2));
	int x = atoi(*(argv + 3));
	int y = atoi(*(argv + 4));
	
	// 棋盘用一维数组其实也行 ，无所谓了 
	int visited[m * n];
	*visited = x * n + y;
	int size = 1;
	
	// 具体得改 
	printf("MAIN: Solving Sonny's knight's tour problem for a %dx%d board\n", m, n);
	printf("MAIN: Sonny starts at row %d and column %d (move #1)\n", x, y);
	
	struct Arg arg = {m, n, size, 0, 0, visited};
	dfs((void *)&arg);
	
	// 具体得改 
	if (total_tours > 0) {
		if (total_tours != 1) {
			printf("MAIN: Search complete; found %d possible paths to achieving a full knight's tour\n", total_tours);
		}
		else {
			printf("MAIN: Search complete; found %d possible path to achieving a full knight's tour\n", total_tours);
		}
	}
	else {
		if (max_squares != 1) {
			printf("MAIN: Search complete; best solution(s) visited %d squares out of %d\n", max_squares, m * n);
		}
		else {
			printf("MAIN: Search complete; best solution(s) visited %d square out of %d\n", max_squares, m * n);
		}
	}
	
	return EXIT_SUCCESS;
	
}

