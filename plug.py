#! /usr/bin/env python2

import gimpcolor
from gimpfu import *
import subprocess
import os
import random
MINIMAX_SUB_DIR = os.path.join("models","mini")


class Sprite: #sprite class
    def __init__(self,scope):       
        self.scope = scope
    
    #layer position on z
    def move_up(self):
        pdb.gimp_image_raise_layer(self.scope,self.obj)
    def move_down(self):
        pdb.gimp_image_lower_layer(self.scope,self.obj)
    def to_bottom(self):
        pdb.gimp_image_lower_item_to_bottom(self.scope,self.obj)
    def to_top(self):
        pdb.gimp_image_raise_layer_to_top(self.scope,self.obj)
    
    def change_color(self,R,G,B):
        color = gimpcolor.RGB(R,G,B)
        pdb.gimp_context_set_foreground(color)   
        pdb.gimp_drawable_edit_fill(self.obj,FILL_FOREGROUND)
        

    def visible(self,v):
        pdb.gimp_layer_set_visible(self.obj,v)
       

    def offset(self,wof,hof):
        pdb.gimp_layer_set_offsets(self.obj,wof,hof)
        

    def rotate(self,angle):
        rotation = (angle/180.0)*3.141592 
        pdb.gimp_item_transform_rotate(self.obj, rotation, True, self.obj.width/2, self.obj.height/2)
       
    def set_ptr(self,ptr):
        self.obj = ptr
        return self

    def find_ptr(self,name):
        self.obj = pdb.gimp_image_get_layer_by_name(self.scope,name)
        return self

    def create_ptr(self,width,height,name,opacity):
        
        temp = pdb.gimp_layer_new(self.scope, width, height, RGBA_IMAGE, name, opacity, NORMAL_MODE)
        pdb.gimp_image_insert_layer(self.scope, temp,None, 1)     
         
        self.obj = temp
        return self





class Game: #game class
    def __init__(self,w,h,img,st):
        self.board = [0]*9
        self.dbn = "DATA"
        self.w = w
        self.h = h
        self.scene = img             
        self.legal = False
        self.starts = st
        self.purged = "CORUPT"
        
        
        self.Game_load()

        
    def Game_load(self):
        self.check_env()
        self.generate_board() 
        self.load_data()
        self.legalize_data()
        self.random_moves()
        self.status()
        self.save_data()
        return

    def get_data_ptr(self):
        for layer in self.scene.layers:
            if layer.name.startswith(self.dbn):
                return layer
        return None

  
        
    def save_data(self):        
        #check if data block exists
        ptr = self.get_data_ptr()
        
        #if not create one
        if ptr is None:
            ptr = pdb.gimp_layer_new(self.scene, 1,1, RGBA_IMAGE, self.dbn, 0, NORMAL_MODE)
            pdb.gimp_image_insert_layer(self.scene, ptr ,None, 1)

        #preserve data for block
        if self.board != self.purged:
            data = str(self.dbn + "?"+ '|'.join(map(str, self.board)) + "?")
        else:
            data = str(self.dbn + "?"+ '|'+self.board+'|' + "?")
        #save current data to data block
        pdb.gimp_item_set_name(ptr,data)

        #exit
        

    def load_data(self):
        #check if is posible to read
        ptr = self.get_data_ptr()
        #if yes read data block
        if ptr is None:
            ptr = pdb.gimp_layer_new(self.scene, 1,1, RGBA_IMAGE, self.dbn, 0, NORMAL_MODE)
            pdb.gimp_image_insert_layer(self.scene, ptr ,None, 1)            
            return   
            
        #load from data block
        raw = ptr.name.split("?")
        board_save = raw[1].split("|")  
          
        if raw[1] == ("|"+self.purged+"|"):
            self.board = [0]*9
        else:
            for i in range(len(board_save)):
                self.board[i] = int(board_save[i])


       
    def legalize_data(self):
        nb = self.get_board()
        old_board = self.board[:]
        self.legal = True
        
        check = 0

        for i in range(len(nb)):
            if nb[i] > self.board[i]:
                self.board[i] = nb[i]
                check += 1

        #check here for errors

        if self.board.count(1) > self.board.count(2)+1:
            self.legal = False
            self.gout("Illegal move")
            self.revert_board(old_board)
            

        #if check == 0 and 1 or 2 in self.board :
            #self.legal = False
            #self.gout("U didnt move")
            
        
        self.fix_board()

    def status(self):
        
        if self.Won(self.board,1) == False:
            if self.Won(self.board,2) == False:  
        
                self.Draw()

    def Draw(self):
        if 0 not in self.board:
            self.gout("Its a draw")            
            for i in range(9):
                Sprite(self.scene).find_ptr("tile"+str(i)).change_color(0,0,255)
            self.board = self.purged
            
    def Won(self,brd,player,show=True):
        l = [
            [0, 1, 2], 
            [3, 4, 5],
            [6, 7, 8],

            [0, 3, 6],
            [1, 4, 7],
            [2, 5, 8],

            [0, 4, 8], 
            [2, 4, 6]
        ]
        for i in range(8):
            a,b,c = l[i]
            if(brd[a]==player and brd[b]==player and brd[c]==player):
                if show is True:
                    Sprite(self.scene).find_ptr("tile"+str(a)).change_color(0,0,255)
                    Sprite(self.scene).find_ptr("tile"+str(b)).change_color(0,0,255)
                    Sprite(self.scene).find_ptr("tile"+str(c)).change_color(0,0,255)

                    if player == 1:
                        self.gout("Congratulations! You won!")
                    elif player == 2:
                        self.gout("You Lost :(")

                    self.board = self.purged
                    return True
        return False
    def random_moves(self):

        if 0 not in self.board or self.legal is not True:
            return
        
        if 1 not in self.board and self.starts == True:
            return

        
        rm = self.minimax(self.board[:])
        if rm is None:
            rm = random.randint(0, 8)
            while self.board[rm] != 0:
                rm = random.randint(0, 8)
        
        self.board[rm] = 2
        tile = Sprite(self.scene).find_ptr(("tile"+str(rm)))
        tile.change_color(255,0,0)
        tile.visible(True)

    def minimax(self,b):
        minimax = os.path.join(os.path.dirname(os.path.abspath(__file__)),MINIMAX_SUB_DIR)
        cmd = minimax+" " + " ".join(map(str,b))
        s = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        return int(s.stdout.read().decode("utf-8"))

    
    def check_env(self):
        if self.scene.width !=self.w or self.scene.height !=self.h:    
                   
            img = gimp.Image(self.w, self.h, RGB)        
            gimp.Display(img)

            self.scene = img
     
    
    def get_board(self):
        read_board = [0]*9
        for layer in self.scene.layers:            
            if pdb.gimp_layer_get_visible(layer) and layer.name.startswith("tile"):
                read_board[int(layer.name[4:])] = 1
        return read_board

    def generate_board(self):    
        if len(self.scene.layers) <= 1:             
            
            rows = 3
            sf = 0.8
            e=0
            tw = self.w/(rows)*sf
            th = self.h/(rows)*sf
        
            

            for i in range(0,rows):
                for j in range(0, rows):
                    #y = y[i] | x = y[j]
                    tile = Sprite(self.scene).create_ptr(tw,th,("tile"+str(e)), 100.00)                 
                    tile.change_color(255,255,0)
                    tile.visible(False)
                    tile.offset(j*(self.w/rows)+((1-sf)/2*tw) ,i*(self.h/rows)+((1-sf)/2*th))
                
                    
                    e+= 1
            pdb.gimp_message(self.scene.layers)
            self.background_create()

    def revert_board(self,old):
        for i in range(len(old)):         
            self.board[i] = old[i]
             
    def background_create(self):
        rows = 3
        sf = 0.9
        e=0
        tw = self.w/(rows)*sf
        th = self.h/(rows)*sf
        for i in range(0,rows):
                for j in range(0, rows):
                    #y = y[i] | x = y[j]
                    tile = Sprite(self.scene).create_ptr(tw,th,("white"+str(e)), 100.00)                 
                    tile.change_color(255,255,255)                    
                    tile.offset(j*(self.w/rows)+((1-sf)/2*tw) ,i*(self.h/rows)+((1-sf)/2*th))
                    tile.to_bottom()
                    e+= 1
        t=Sprite(self.scene).create_ptr(self.w,self.h,("background"), 100.00)
        t.change_color(0,0,0)
        t.to_bottom()
        

    def fix_board(self):
        for i in range(len(self.board)):
            t = Sprite(self.scene).find_ptr("tile"+str(i))
            if self.board[i] == 0:
                t.change_color(255,255,0)
                t.visible(False)
            elif self.board[i] == 1:
                t.change_color(255,255,0)
                t.visible(True)
            elif self.board[i] == 2:
                t.change_color(255,0,0)
                t.visible(True)

    def gout(self,text):
        pdb.gimp_message(text)
    





def loop(imag,drawable,starts):    
    Game(600,600,imag,starts)   

    return


register(
    "Gra",#name
    "epic games",#opisus
    "this game is kinda epic",#short opisus
    "Ignacy",# maj name
    "Ignacy Bu",#maj full name
    "2021",#rok
    "<Image>/Gamez/tic-tac-toe",# z kond otworzyc
    "*",
    [
        (PF_BOOL,"starts","Player starts : ",1),        
        
        
    ],#variables
    [],
    loop#funkcja wlaczana
)

main()
