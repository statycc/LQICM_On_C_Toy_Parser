int main()
{
  int i;
  int fact;
  srand(time(NULL));
  int n = rand() % 100;
  int j = 0;
  fact = 1;
  i = 1;
  if (j < 100)
  {
    fact_1 = 1;
    i_1 = 1;
    while (i < n)
    {
      fact = fact * i;
      i = i + 1;
    }

    j = j + 1;
  }

  while (j < 100)
  {
    j = j + 1;
  }

  printf("blabla %d %d", i, fact);
  return i;
}


