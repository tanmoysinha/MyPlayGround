#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>

#define EXIT_FAILURE 1

int main()
{
    int optval;
    int sv[2];
    socklen_t optlen = sizeof(optval);

    if (socketpair(AF_UNIX, SOCK_DGRAM, 0, sv) < 0) {
        perror("Socketpair creation failed");
        exit(EXIT_FAILURE);
    }

    if (getsockopt(sv[0], SOL_SOCKET, SO_RCVBUF, &optval, &optlen) < 0) {
        perror("getsockopt()");
        exit(EXIT_FAILURE);
    }

    printf("sv[0] RCVBUF: %d\n", optval);

    if (getsockopt(sv[0], SOL_SOCKET, SO_SNDBUF, &optval, &optlen) < 0) {
        perror("getsockopt()");
        exit(EXIT_FAILURE);
    }

    printf("sv[0] SNDBUF: %d\n", optval);


    if (getsockopt(sv[1], SOL_SOCKET, SO_RCVBUF, &optval, &optlen) < 0) {
        perror("getsockopt()");
        exit(EXIT_FAILURE);
    }

    printf("sv[1] RCVBUF: %d\n", optval);

    if (getsockopt(sv[1], SOL_SOCKET, SO_SNDBUF, &optval, &optlen) < 0) {
        perror("getsockopt()");
        exit(EXIT_FAILURE);
    }

    printf("sv[1] SNDBUF: %d\n", optval);

    printf("Ptr Size: %d\n", sizeof(void *));

    return 0;
}
