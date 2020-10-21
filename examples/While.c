int main(){
    int a,b,c,d,e,f;
    a = 0;
    b = 42;
    c = 90;
    d = 1;
    e = 0;
    f = 0;

    while(d<100){
        a = b;
        b = c;
        c = 90;
        if(f == 10 ){
            c = -5;
        }
        if(e == 10 ){
            c = 0;
        }
        e = 60;
        d = d + 1;
    }
}
