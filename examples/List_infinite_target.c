int main(){
    int i = 0, a = 0, b = 0, c = 0;
    int array[100];
    while(i<100){
        a = b;
        b = c;
        array[i] = a;
        c = 90;
        i = i +1;
    }
}
