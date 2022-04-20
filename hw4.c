#include <sys/types.h>
#include <string.h>
#include <stdlib.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <netdb.h>
#include <stdio.h>
#include <strings.h>
#include <unistd.h>

#define MAXBUFFER 1024

int judge_parameter(int argc, char** argv);

void print_error();

int main(int argc, char** argv) {
	
	int result_parameter = judge_parameter(argc, argv);
	
	if (result_parameter == 0) {
		print_error();
		return EXIT_FAILURE;
	}
	
	char *server_name = argv[1];
	unsigned short server_port = (unsigned short)atoi(argv[2]);
	int n = atoi(argv[3]);
	
	int num[n];
	int i = 0;
	for (i = 0; i < n; i++) {
		num[i] = atoi(argv[i + 4]);
	}
	
	int sd = socket( AF_INET, SOCK_STREAM, 0 );
	if (sd == -1) {
        perror("Error: socket() failed\n");
        exit(EXIT_FAILURE);
    }
    
    struct hostent *hp = gethostbyname(server_name);
    if ( hp == NULL ) {
	    perror( "ERROR: gethostbyname() failed\n" );
	    return EXIT_FAILURE;
	}
	
	struct sockaddr_in tcp_server;
    tcp_server.sin_family = AF_INET;
    memcpy( (void*)&tcp_server.sin_addr, (void *)hp -> h_addr, hp -> h_length );
    tcp_server.sin_port = htons( server_port );
    
	if (connect(sd, (struct sockaddr *)&tcp_server, sizeof(tcp_server))) {
        perror("Error: connect() failed\n");
        close(sd);
        return EXIT_FAILURE;
    }
    printf("CLIENT: Successfully connected to server\n");
 
	if (n == 1) {
		printf("CLIENT: Sending 1 integer value\n");
	}
	else {
		printf("CLIENT: Sending %d integer values\n", n);
	}
	
	unsigned int num_send[n + 1];
	num_send[0] = htonl(n);
	for (i = 0; i < n; i++) {
		num_send[i + 1] = htonl(num[i]);
	}
	
	int result_1 = write(sd, &num_send, sizeof(unsigned int) * (n + 1));
    if (result_1 == -1) {
        perror("Error: write() failed\n");
        close(sd);
        return EXIT_FAILURE;
    }
    
    short integer_recv;
    result_1 = read(sd, &integer_recv, sizeof(integer_recv));
    if (result_1 == -1) {
        perror("Error: read() failed\n");
        close(sd);
        return EXIT_FAILURE;
    }
    else if (result_1 == 0) {
	    printf( "CLIENT: Rcvd no data; TCP server socket was closed\n" );
	} 

    else {
    	integer_recv = ntohs(integer_recv);
    	printf("CLIENT: Rcvd result: %d\n", integer_recv);
    }
    
    char secret_message[MAXBUFFER + 1];
    int index = 1;
    
	while (1) {
		result_1 = read(sd, secret_message, MAXBUFFER);
	    if (result_1 == -1) {
	    	perror("Error: read() failed\n");
	        close(sd);
	        return EXIT_FAILURE;
	    }
	    
	    else if (result_1 == 0) {
	    	break;
	    	//printf( "CLIENT: Rcvd no data; TCP server socket was closed\n" );
	    } 
	    
	    else {
	    	secret_message[result_1] = '\0';
		    printf("CLIENT: Rcvd secret message #%d: \"%s\"\n", index, secret_message);
		    index++;
		}
	    
	}
  
	close(sd);
	printf("CLIENT: Disconnected from server\n");
  	return EXIT_SUCCESS;
}

int judge_parameter(int argc, char** argv) {
	
	if (argc < 3 || argc - 4 != atoi(argv[3])) {
		return 0;
	}
	
	//char *server_name = argv[1];
	//unsigned short server_port = (unsigned short)atoi(argv[2]);
	int n = atoi(argv[3]);
	
	if (strcmp(argv[3], "0") != 0 && n == 0) {
		return 0;
	}
	
	if (n < 0) {
		return 0;
	}
	
	return 1;	
}

void print_error(int argc, char** argv) {
	
	fprintf(stderr, "ERROR: Invalid argument(s)\n");
    fprintf(stderr, "USAGE: a.out <server-hostname> <server-port> <n> <int-value-1> ... <int-value-n>\n");
	return;
	
}

