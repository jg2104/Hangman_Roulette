from tkinter import ttk
from tkinter import Canvas
from tkinter import messagebox
import customtkinter as ctk
from PIL import Image, ImageTk
import random
import time
from wordfreq import top_n_list

#To set the display
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

#Creates window, dimensions, prevents window size change
root=ctk.CTk() 
root.title("Hangman Roulette")
root.geometry('750x750')
root.resizable(False,False) 

#Global variables
lives=6
guessed_letters=[]
secret_word = ''
word_blank = ''
WORD_POOL = top_n_list("en", 5000)
used_words = set()
image_ref=[]
safe=False  #becomes true when result is safe
double=False #becomes true when result is double
double_done=False #becomes true when double is over

#Loading and making list of hangman images
imgs=["hangman0.png","hangman1.png","hangman2.png","hangman3.png","hangman4.png","hangman5.png","Default.png"]
for i,img in enumerate(imgs):
    Img=Image.open(img) #Opens image using PIL
    photo_img=ImageTk.PhotoImage(Img) #To create a Tkinter compatible image
    image_ref.append(photo_img)
    
#Loading wheel image
wheel_img=Image.open("wheel.png")
width,height=wheel_img.size[0],wheel_img.size[1] #.size returns tuple(w,h)

#Canvas creation(Used to draw and animate objects here wheel)
canvas=Canvas(root,width=width,height=height,bg=root["bg"],highlightthickness=0)
canvas.pack()

#Open wheel image
photo=ImageTk.PhotoImage(wheel_img)
wheel=canvas.create_image(width//2, height//2, image=photo)
canvas.image=photo

def spin_wheel():
    sections=["Lose", "Gain", "Death", "Double", "Reveal", "Safe"]
    total_degrees=random.randint(1080, 1800) #goes for 3 to 5 cycles
    current_angle=0
    speed=20
    #To show spinning
    for i in range(3):
        result_display.configure(text="SPINNING" + "." * (i+1))
        root.update()
        time.sleep(0.2)
    while current_angle < total_degrees:
        rotated_img = wheel_img.rotate(-current_angle)
        tk_img = ImageTk.PhotoImage(rotated_img)

        canvas.itemconfig(wheel, image=tk_img)
        canvas.image=tk_img

        current_angle+=speed
        if total_degrees-current_angle < 300:
                speed=max(2, speed - 1)

        root.update()
        time.sleep(0.01)
    
    final_angle=current_angle % 360
    section_index=int(final_angle // 60) % 6
    result = sections[section_index]
    
    
    colors = {"Lose": "#FF4444", "Gain": "#44FF44", "Death": "#444444", "Double": "#FFAA00", "Reveal": "#44AAFF", "Safe": "#AA44FF"}
    
    for i in range(5):
        result_display.configure(text=result.upper(), text_color=colors[result])
        root.update()
        time.sleep(0.1)
        result_display.configure(text=" " * len(result))
        root.update()
        time.sleep(0.1)
    
    result_display.configure(text=result.upper(), text_color=colors[result])
    
    return result

#To show result of wheel spin
result_display=ctk.CTkLabel(root,text="",font=("Arial",32,"bold"))
result_display.pack(pady=10)

def get_new_word():
    global secret_word,word_blank,guessed_letters
    while True:
        word = random.choice(WORD_POOL)
        if len(word)>=4 and word.isalpha() and word not in used_words:
            used_words.add(word)
            secret_word = word.lower()
            word_blank = '_' * len(secret_word)
            guessed_letters = []
            return secret_word

get_new_word()

def make_guess(letter):
    ans=check_guess(letter,secret_word)
    if ans=="Error":
        return
    update_guessed_display()
    
    if "_" in word_blank and lives > 0:
        result = spin_wheel()
        apply_wheel_consequence(result)
    
    check_game_over()

def check_guess(letter, word):
    global lives, word_blank, guessed_letters,safe, double, double_done

    if letter in guessed_letters:
        messagebox.showinfo("Error", "Already guessed.")
        return "Error"

    guessed_letters.append(letter)

    if letter in word:
        word_list = list(word_blank)
        for i, j in enumerate(word):
            if j == letter:
                word_list[i] = letter
        word_blank = "".join(word_list)

        safe=False,double = False,double_done = False

        update_word_display()
        return True

    if safe:
        safe = False
        return False

    if double:
        if not double_done:
            double_done = True
            return False
        else:
            double = False
            double_done = False

    lives -= 1
    update_hangman_drawing(lives)
    return False

word_display = ctk.CTkLabel(root, text='', font=('Arial', 24))
word_display.pack()

def update_word_display():
    display_text = ' '.join(word_blank)
    word_display.configure(text=display_text)

hangman_status = ctk.CTkLabel(root, text=f"Lives: {lives}", font=('Arial', 16))
hangman_status.pack()

guessed_label = ctk.CTkLabel(root, text="Guessed: ", font=('Arial', 14))
guessed_label.pack()

def update_guessed_display():
    guessed_label.configure(text=f"Guessed: {', '.join(sorted(guessed_letters))}")

def apply_wheel_consequence(result):
    global lives, word_blank, guessed_letters,safe, double, double_done

    if result == "Safe":
        safe = True,double = False,double_done = False
    elif result == "Double":
        double = True,double_done = False,safe = False
    elif result == "Death":
        lives = 0
        update_hangman_drawing(lives)
        check_game_over()

    elif result == "Gain":
        lives += 1
        update_hangman_drawing(lives)

    elif result == "Lose":
        lives -= 1
        update_hangman_drawing(lives)
        check_game_over()

    elif result == "Reveal":
        unrevealed=[]
        for i,l in enumerate(secret_word):
            if  word_blank[i] == '_':
                unrevealed.append(i)
        if unrevealed:
            idx = random.choice(unrevealed)
            letter = secret_word[idx]
            if letter not in guessed_letters:
                guessed_letters.append(letter)
            word_list = list(word_blank)
            word_list[idx] = letter
            word_blank = "".join(word_list)
            update_word_display()
            update_guessed_display()

def check_game_over():
    if "_" not in word_blank:
        messagebox.showinfo("You have guessed the word!")
        reset_game()
    elif lives <= 0:
        messagebox.showinfo("Game Over", f"You lost.The word was: {secret_word}")
        reset_game()

def reset_game():
    global lives, guessed_letters,safe,double,double_done
    lives = 6
    guessed_letters = []
    safe=False
    double=False
    double_done=False
    get_new_word()
    update_word_display()
    update_hangman_drawing(lives)
    update_guessed_display()
    result_display.configure(text="")
    # Reset wheel to original position
    original_photo = ImageTk.PhotoImage(wheel_img)
    canvas.itemconfig(wheel, image=original_photo)
    canvas.image=original_photo
#make letter buttons
letters_frame = ctk.CTkFrame(root)
letters_frame.pack(pady=10)
def create_letter_buttons():
    for i in range(26):
        letter = chr(ord('a') + i)
        btn = ctk.CTkButton(letters_frame, text=letter.upper(), width=50, height=40,command=lambda l=letter: make_guess(l))
        btn.grid(row=i//13, column=i%13, padx=2, pady=2)
#To display hangman drawings      
frame=ttk.Frame(root, width=300, height=300)
hangman=ttk.Label(frame,image=image_ref[6])
frame.pack()
hangman.pack()
def update_hangman_drawing(lives):
    if lives <= 0:
        check_game_over()
    hangman.configure(image=image_ref[max(0,min(lives,6))])
    hangman_status.configure(text=f"Lives: {lives}")
    hangman.pack()

newgame = ctk.CTkButton(root, text="NEW GAME", font=('Arial', 14),command=reset_game)
newgame.pack(pady=5)

#Info button that will display rules
def info():
    messagebox.showinfo("Rules",'''Welcome to Hangman Roulette!
Hangman Roulette is a twist on the classic Hangman game, combined with a roulette wheel that adds a surprise outcome to every turn.

A word is chosen at the start of the game.
Players take turns guessing one letter at a time.
Each player starts with a fixed number of *lives*.

1. The player guesses a letter.
2. The player spins the roulette wheel.
3. The wheel lands on one of the following options:
   Safe: If the player guesses wrong, they do not lose a life.
   Double: If the player guesses wrong, they get one extra chance without losing a life.
            If they guess wrong again, they lose one life.
   Lose: The player loses one life
   Gain: The player gains one life.
   Death: The player loses all lives instantly and is eliminated from the game.
   Reveal: One hidden letter is revealed in the word.
4. The effect of the roulette option is applied based on the guess.

Winning the Game
* Players win by successfully guessing all the letters in the word.
* Players are lose when they lose all their lives.

Good luck, spin wisely, and may the wheel be in your favor!''')
    
Img=Image.open("information.png")
i=ctk.CTkImage(Img)
info_button = ctk.CTkButton(root,width=10, height=10,fg_color="transparent", text="",image=i, font=('Arial', 14),command=info)
info_button.place(relx=1.0, rely=0.0,anchor="ne", x=-10, y=10)

# Initialize display
update_word_display()
update_hangman_drawing(lives)
create_letter_buttons()

root.mainloop()
