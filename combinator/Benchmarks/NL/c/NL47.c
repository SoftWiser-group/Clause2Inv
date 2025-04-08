int main(){
    int x, y;
    int q, a, b; 

    assume(x >= 0);
    assume(y >= 1);
    q = 0;
    a = 0;
    b = x;

    while(b != 0) {
        if (a + 1 == y) {
            q = q + 1;
            a = 0;
            b = b - 1;
        }
        else {
            a = a + 1;
            b = b - 1;
        }
    }

    assert(q == x / y);
}