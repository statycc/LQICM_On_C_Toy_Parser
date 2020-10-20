int main()
{
  int a;
  int b;
  int c;
  int d;
  int e;
  a = 0;
  b = 42;
  c = 90;
  d = 1;
  e = 0;
  if (e < 100)
  {
    a = b;
    b = c;
    c = 90;
    a = 10;
    d = e + d;
    if (d < 100)
    {
      a = 10;
      d = e + d;
    }

    while (d < 100)
    {
      d = e + d;
    }

    e = e + 1;
  }

  if (e < 100)
  {
    a = b;
    b = c;
    d = e + d;
    if (d < 100)
    {
      a = 10;
      d = e + d;
    }

    while (d < 100)
    {
      d = e + d;
    }

    e = e + 1;
  }

  if (e < 100)
  {
    a = b;
    d = e + d;
    if (d < 100)
    {
      a = 10;
      d = e + d;
    }

    while (d < 100)
    {
      d = e + d;
    }

    e = e + 1;
  }

  while (e < 100)
  {
    d = e + d;
    if (d < 100)
    {
      a = 10;
      d = e + d;
    }

    while (d < 100)
    {
      d = e + d;
    }

    e = e + 1;
  }

}


