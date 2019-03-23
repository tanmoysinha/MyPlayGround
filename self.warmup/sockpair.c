#include <errno.h>
#include <stdint.h>
#include <stdio.h>
#include <sys/socket.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>

#define SOCKPAIR_READER 0
#define SOCKPAIR_WRITER 1

    int
main(void)
{
    int optval;
    int sv[2];
    socklen_t optlen = sizeof(optval);
    int i;

    if (socketpair(AF_UNIX,  SOCK_DGRAM| SOCK_NONBLOCK, 0, sv) < 0)
    {
        perror("socketpair");
        return -1;
    }

#if 1
    /* Shutdown read on writer socket */
    if (shutdown(sv[SOCKPAIR_READER], SHUT_WR) < 0)
    {
        perror("shutdown SOCKPAIR_READER");
        return -1;
    }

    /* Shutdown read on writer socket */
    if (shutdown(sv[SOCKPAIR_WRITER], SHUT_RD) < 0)
    {
        perror("shutdown SOCKPAIR_WRITER");
        return -1;
    }
#endif

    for (i = SOCKPAIR_READER; i <= SOCKPAIR_WRITER; i++) {

        if (getsockopt(sv[i], SOL_SOCKET, SO_RCVBUF, &optval, &optlen) < 0) {
            perror("getsockopt()");
            exit(EXIT_FAILURE);
        }

        printf("sv[%d] RCVBUF: %d\n", i, optval);
        optval = 0;

        if (getsockopt(sv[i], SOL_SOCKET, SO_SNDBUF, &optval, &optlen) < 0) {
            perror("getsockopt()");
            exit(EXIT_FAILURE);
        }

        printf("sv[%d] SNDBUF: %d\n", i, optval);
    }

#if 1
    int snd_buf = 1024*1024; //1 MB

    if(setsockopt(sv[SOCKPAIR_READER], SOL_SOCKET,
                SO_RCVBUF, &snd_buf, sizeof(snd_buf)) < 0) {
        perror("setsockopt()");
        exit(EXIT_FAILURE);
    }

    if(setsockopt(sv[SOCKPAIR_WRITER], SOL_SOCKET,
                SO_SNDBUF, &snd_buf, sizeof(snd_buf)) < 0) {
        perror("setsockopt()");
        exit(EXIT_FAILURE);
    }

    for (i = SOCKPAIR_READER; i <= SOCKPAIR_WRITER; i++) {

        if (getsockopt(sv[i], SOL_SOCKET, SO_RCVBUF, &optval, &optlen) < 0) {
            perror("getsockopt()");
            exit(EXIT_FAILURE);
        }

        printf("sv[%d] RCVBUF: %d\n", i, optval);
        optval = 0;

        if (getsockopt(sv[i], SOL_SOCKET, SO_SNDBUF, &optval, &optlen) < 0) {
            perror("getsockopt()");
            exit(EXIT_FAILURE);
        }

        printf("sv[%d] SNDBUF: %d\n", i, optval);
    }
#endif

    uint64_t counter = 0;
    char *addr = "Hello World let us get into a mess";

    while(send(sv[SOCKPAIR_WRITER], addr, sizeof(addr), 0) == sizeof(addr))
    {
        ++counter;
    }
    printf("Errno %d, Counter: %llu\n", errno, counter);

    return 0;
}
