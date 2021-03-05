int main()
{
  int i = 0;
  int a = 0;
  int b = 0;
  int c = 0;
  int array[100];
  if (i < 100)
  {
    a = b;
    b = c;
    array[b] = a;
    c = 90;
    i = i + 1;
  }

  if (i < 100)
  {
    a = b;
    b = c;
    array[b] = a;
    i = i + 1;
  }

  if (i < 100)
  {
    a = b;
    array[b] = a;
    i = i + 1;
  }

  while (i < 100)
  {
    i = i + 1;
  }

}


