int main() {
    int n;          
    int guess;      
    int prev_guess; 
    assume(n > 0);   
    guess = n / 2;  
    prev_guess = 0; 

    while (guess != prev_guess) {
        prev_guess = guess;
        guess = (guess + n / guess) / 2;  
    }
    
    assert(guess * guess <= n);
}
