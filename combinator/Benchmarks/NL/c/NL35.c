int main() { 
  int x,y,u,v,a,b;

  //pre-condition
  x=a;
  y=b;
  u=b;
  v=0;
  assume(a >= 1);
  assume(b >= 1);

  //loop-body
  while(x!=y) {
    if (x>y){
        x=x-y;
        v=v+u;
    }
    else {
        y=y-x;
        u=u+v;
    }
  }

  //post-condition
  assert(x*u + y*v == a*b);
}   
