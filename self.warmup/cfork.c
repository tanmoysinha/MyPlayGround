#include <stdio.h>
#include <unistd.h>
#include <signal.h>

int main()
{
    int id;
    printf("Hello, World!\n");
    signal(SIGCHLD, SIG_IGN);
    id=fork();
    if(id>0)
    {
        /*parent process*/
        printf("This is parent section [Process id: %d].\n",getpid());
        sleep(120);
    }
    else if(id==0)
    {
        /*child process*/
        printf("fork created [Process id: %d].\n",getpid());
        printf("fork parent process id: %d.\n",getppid());
        sleep(10);
        printf("Exiting child [Process id: %d].\n",getpid());
    }
    else
    {
        /*fork creation faile*/
        printf("fork creation failed!!!\n");
    }

    return 0;
}
