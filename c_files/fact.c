int main(){
    int i, fact;
    srand(time(NULL));
    int n=rand()%100;
    int j=0; 
    fact=1; 
    i=1;
    while(j<100){
        fact=1;
        i=1;
        while (i<n) { 
            fact=fact*i; 
            i=i+1;
        }
        j=j+1;
    }
    printf("blabla %d %d", i, fact);
    return i;
}
