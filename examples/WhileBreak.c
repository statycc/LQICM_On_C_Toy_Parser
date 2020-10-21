int main(){
    int a,b,c,d;
    a = 0;
    b = 42;
    c = 90;
    d = 1;
    while(d < 100){
        a = b * c + 10;
        b = c + 5;
        c = 90;
        if (a == 90)
        {
            c = 100;
            break;
        }
        d = d + 1;
    }
}
