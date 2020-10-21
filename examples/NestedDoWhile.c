int main(){
    int a,b,c,d,e;
    a=0;
    b=42;
    c = 90;
    d = 1;
    e = 0;
    while(e < 100){
        a = b;
        b = c;
        c = 90;
        do{
            a = 10;
            d = e + d;
        }while(d < 100);
        e = e + 1;
    }

}
