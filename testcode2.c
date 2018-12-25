#include <stdio.h>
int x;
int main()
{
	int a = 10;
	int b;
	b = 20;
	int c;
	c = a + b;
	int *p;
	p = &a;
	*p = 40;
	p = &b;
	*p = 50;
}