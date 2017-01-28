void use(int y)
{
  printf("y=%d\n", y);
}

int main()
{
  int i = 0;
  int y = 0;
  srand(time(NULL));
  int x = rand() % 100;
  int x2 = rand() % 100;
  int z;
  if (i < 100)
  {
    z = y_1 * y_1;
    use(z);
    y = x + x;
    use(y);
    x = x2;
    use(x);
  }

  if (i < 100)
  {
    z = y_1 * y_1;
    use(z);
    use(y);
    use(x);
  }

  while (i < 100)
  {
    use(z);
    use(y);
    use(x);
  }

  return 42;
}


