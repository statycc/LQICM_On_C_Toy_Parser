int main(){
    int a,b,c,d;
    a = 0;
    b = 42;
    c = 90;
    d = 1;
    while(d < 100){
        a = b;
        b = c;
        c = 90;
        d = d + 1;
    }
    for(int i  = 0 ; i < a; i++)
    {
        a = b;
        b = c;
        c = 90;
        d = d + 1;
    }
}

