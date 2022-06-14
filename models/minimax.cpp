#include <iostream>
#include <vector>
using namespace std;

bool Won(int player,int board[])
{
    int l[8][3]={
        
        {0, 1, 2}, 
        {3, 4, 5},
        {6, 7, 8},

        {0, 3, 6},
        {1, 4, 7},
        {2, 5, 8},

        {0, 4, 8}, 
        {2, 4, 6}
    };

    for(int i=0;i<9;i++){
        int a=l[i][0],b=l[i][1],c=l[i][2];

        if (board[a]==player && board[b]==player && board[c]==player)
            return true;
    }
    return false;
}

bool Draw(int board[]){
    for (int i=0;i<9;i++)
    {
        if (board[i] == 0)
            return false;
    }
    return true;
}

struct pred{
    int move;
    int value;
};


int hu = 1;
int ai = 2;

pred minimax(int board[],bool MAX)
{
    pred Result;
    
    if (Won(hu,board)){
        Result.value = -10;
        return Result;
    }
        
    if (Won(ai,board)){
        Result.value = 10;
        return Result;
    }
        
    if (Draw(board)){
        Result.value = 0;
        return Result;
    }
        



    pred best;
    best.value = (MAX)?-100:100;

    for (int i=0;i<9;i++)
    {
        if (!board[i]){
            
            if (MAX){//ai
                board[i] = ai;
                pred o;
               
                o.value= minimax(board,!MAX).value;
               
                if(o.value > best.value)
                {
                    best.move = i;
                    best.value = o.value;
                }                
                             
            }
            else{//hu
                board[i] = hu;
                pred o;
                o.value= minimax(board,!MAX).value;
                
                if(o.value < best.value)
                {
                    best.move = i;
                    best.value = o.value;
                }  
            }
            board[i] = 0;
        }
    }
    return best;
}



int main(int argc, char **argv){
    int b[9];
    

    for(int i=0;i<9;i++)
        b[i] =  int(argv[i+1][0])-48;
    
   
    cout << minimax(b,true).move;
}