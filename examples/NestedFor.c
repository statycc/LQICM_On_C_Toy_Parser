int main(){
    int a,b,c,d,e;
    a = 0;
    b = 4;
    c = 90;
    d = 1;
    e = 50;
    while(d < e){
        a = b;
        b = c;
        c = 90;
        for(int i = 0; i < d ;i++){
            a = 50;
            e = e - 1;
        }
        d = d + 1;
    }

}
