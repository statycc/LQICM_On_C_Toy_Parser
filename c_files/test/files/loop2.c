void use(int y){
    printf("y=%d\n",y);
}

int main(){
    int i=0,y=0;
    srand(time(NULL));
    int x=rand()%100;
    int x2=rand()%100;
    int z;
    while(i<100){
        z=y*y;
        use(z);
        y=x+x;
        use(y);
        x=x2;
        use(x);
    }
    return 42;
}
