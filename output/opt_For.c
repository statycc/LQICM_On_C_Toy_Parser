int main()
{
  int a;
  int b;
  int c;
  int d;
  a = 0;
  b = 42;
  c = 90;
  d = 1;
  int i = 0;
  if (i < a)
  {
    a = b;
    b = c;
    c = 90;
    d = d + 1;
    i++;
  }

  if (i < a)
  {
    a = b;
    b = c;
    d = d + 1;
    i++;
  }

  if (i < a)
  {
    a = b;
    d = d + 1;
    i++;
  }

  while (i < a)
  {
    d = d + 1;
    i++;
  }

}


