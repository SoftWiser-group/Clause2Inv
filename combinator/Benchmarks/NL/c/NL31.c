//sum01-1.c
int main() { 
  int i, n, sn, a;

  assume(n > 0);

  //pre-condition
  sn = 0;
  i = 0;

  //loop-body
  while(i < n) {
    sn = sn + a;
    i++;
  }

  //post-condition
  assert(sn == n*a || sn == 0);
}
