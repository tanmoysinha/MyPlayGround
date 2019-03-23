#include <stdio.h>
#include <string.h>
#include <malloc.h>

int main(void)
{
    char *v1 = "3.1.0.43";
    char *v2 = "3.1.500.4";

    char *v1_tmp = strdup(v1);
    char *v2_tmp = strdup(v2);
    char *ptr;

    ptr = strrchr(v1_tmp, '.');
    *ptr = '\0';
    ptr = strrchr(v2_tmp, '.');
    *ptr = '\0';

    int rc = strverscmp(v1_tmp, v2_tmp);
    printf("%s comp %s : %d\n", v1_tmp, v2_tmp, rc);
    free(v1_tmp);
    free(v2_tmp);
    return 0;
}
