//ps5
int main(){
     // variable declarations
     int k,y,x,c;
     //precondition
     assume( k>= 0 );
     assume( k <= 30 );
     assume( y == 0 );
     assume( x == 0 );
     assume( c = 0 );

     // loop body
     while(c < k){
	  c = c +1 ;
	  y = y +1;
	  x = y*y*y*y+x;
     }

     // post-condition
     assert(6*k*k*k*k*k + 15*k*k*k*k+ 10*k*k*k - 30*x - k == 0);
}
