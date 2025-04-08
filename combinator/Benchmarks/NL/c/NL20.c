//sqrt1
int main(){
     // variable declarations
     int n,a,s,t;

     //precondition
     assume(n >= 0);
     assume(a==0);
     assume(s==1);
     assume(t==1);

     // loop body
     while(s <= n){
	  a=a+1;
	  t=t+2;
	  s=s+t;
     }

     // post-condition
     assert( n < (a + 1) * (a + 1));
}
