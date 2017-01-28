int main()
{
  int y = 1;
  int x = 0;
  int b = 0;
  if (x < 100)
  {
    b_1 = b_1 + 1;
    x = x + 1;
    y = 0;
    while (y < 100)
    {
      b = a + y;
      c = b + a;
      y = y * y;
      y = y + 1;
    }

    use(b);
  }

  if (x < 100)
  {
    b_1 = b_1 + 1;
    x = x + 1;
    use(b);
  }

  while (x < 100)
  {
    x = x + 1;
    use(b);
  }

}


