int main(){
    int i,x,y,z;
    i=0;
    x=42;
    y=5;
    while(i<100){
        j=0;
        s=1;
        while (j<y) { 
            s=s*j; 
            j=j+1;
        }
        if (x>100) {
	    y=x+1;
	}
	if (x<=100) {
	    y=x+100;
	}
        j=i+1;
	i=j+0;
    }
    printf("blabla %d %d", i, y);
    return i;
}
