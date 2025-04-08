//ps3
int main(){
     // variable declarations
     int k,y,x,c;

     //precondition
     assume( k >= 0 );
     assume( k <= 30 );
     assume( y == 0 );
     assume( x == 0 );
     assume( c == 0 );


     // loop body
     while(c < k){
	  c = c + 1;
	  y = y + 1;
	  x = y * y + x;
     }
     // post-condition
     assert(6*x-2*k*k*k-3*k*k-k == 0);
}
