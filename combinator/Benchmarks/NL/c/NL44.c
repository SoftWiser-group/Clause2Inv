//freire1.c
int main(){
     // variable declarations
    int x, a, r;
     //precondition
    assume(a % 2 == 0);
    assume(a > 0);
    r = 0;
    x = a / 2;

     // loop body
    while (x > r){
        x = x - r;
        r = r + 1;
    }
     // post-condition
     assert(a == 2*x + r*r - r);
}

