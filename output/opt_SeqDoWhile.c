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
  c = 90;
  b = c;
  a = b;
  if (d < 100)
  {
    c = 90;
    b = c;
    a = b;
  }

  while (d < 100)
  {
  }

  if (d < 100)
  {
    a = b;
    b = c;
    c = 90;
    d = d + 1;
  }

  if (d < 100)
  {
    a = b;
    b = c;
    d = d + 1;
  }

  if (d < 100)
  {
    a = b;
    d = d + 1;
  }

  while (d < 100)
  {
    d = d + 1;
  }

}


