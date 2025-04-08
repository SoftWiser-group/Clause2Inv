int main() { 
  int u,v,r,A,R;

  //pre-condition
  u=2*R+1;
  v=1;
  r=R*R-A;
  assume(A >= 1);
  assume((R-1)*(R-1) < A);
  assume(A <= R*R);
  assume(A%2 ==1); 

  //loop-body
  while(r>0) {
    r=r-v;
    v=v+2;
  }

  //post-condition
  assert(4*(A+r) == u*u-v*v-2*u+2*v);
}   
