from tkinter import *

root = Tk()
root.title("Calculator")

Operator = ""
TextIn = StringVar()

def BtnClick(Intergers):
    global Operator
    Operator = Operator + str(Intergers)
    TextIn.set(Operator)

def BtnClear():
    global Operator
    Operator = ""
    TextIn.set("")

def BtnEquals():
    global Operator
    Sum = str(eval(Operator))
    TextIn.set(Sum)
    Operator = ""

TxtDisplay = Entry(root, font=('arial', 20, 'bold'), textvariable=TextIn, bd=30,
                   insertwidth=4, bg="powder blue", justify='right').grid(columnspan=4)

#======================================================Top Row=================================================================================================
Btn7 = Button(root, padx=16, bd=8, fg="black", bg="powder blue", font=('arial', 20, 'bold'), text="7", command=lambda:BtnClick(7)).grid(row=1, column=0)
Btn8 = Button(root, padx=16, bd=8, fg="black", bg="powder blue", font=('arial', 20, 'bold'), text="8", command=lambda:BtnClick(8)).grid(row=1, column=1)
Btn9 = Button(root, padx=16, bd=8, fg="black", bg="powder blue", font=('arial', 20, 'bold'), text="9", command=lambda:BtnClick(9)).grid(row=1, column=2)
Addition = Button(root, padx=16, bd=8, fg="black", bg="powder blue", font=('arial', 20, 'bold'), text="+", command=lambda:BtnClick("+")).grid(row=1, column=3)
#======================================================Mid Row=================================================================================================
Btn4 = Button(root, padx=16, bd=8, fg="black", bg="powder blue", font=('arial', 20, 'bold'), text="4", command=lambda:BtnClick(4)).grid(row=2, column=0)
Btn5 = Button(root, padx=16, bd=8, fg="black", bg="powder blue", font=('arial', 20, 'bold'), text="5", command=lambda:BtnClick(5)).grid(row=2, column=1)
Btn6 = Button(root, padx=16, bd=8, fg="black", bg="powder blue", font=('arial', 20, 'bold'), text="6", command=lambda:BtnClick(6)).grid(row=2, column=2)
Subtraction = Button(root, padx=16, bd=8, fg="black", bg="powder blue", font=('arial', 20, 'bold'), text="-", command=lambda:BtnClick("-")).grid(row=2, column=3)
#======================================================Bot Row==================================================================================================
Btn1 = Button(root, padx=16, bd=8, fg="black", bg="powder blue", font=('arial', 20, 'bold'), text="1", command=lambda:BtnClick(1)).grid(row=3, column=0)
Btn2 = Button(root, padx=16, bd=8, fg="black", bg="powder blue", font=('arial', 20, 'bold'), text="2", command=lambda:BtnClick(2)).grid(row=3, column=1)
Btn3 = Button(root, padx=16, bd=8, fg="black", bg="powder blue", font=('arial', 20, 'bold'), text="3", command=lambda:BtnClick(3)).grid(row=3, column=2)
Multiply = Button(root, padx=16, bd=8, fg="black", bg="powder blue", font=('arial', 20, 'bold'), text="*", command=lambda:BtnClick("*")).grid(row=3, column=3)
#=====================================================Func Row==================================================================================================
Btn0 = Button(root, padx=16, pady=0, bd=8, fg="black", bg="powder blue", font=('arial', 20, 'bold'), text="0", command=lambda:BtnClick(0)).grid(row=4, column=0)
BtnClear = Button(root, padx=16, pady=0, bd=8, fg="black", bg="powder blue", font=('arial', 20, 'bold'), text="C", command=BtnClear).grid(row=4, column=1)
BtnEquals = Button(root, padx=16, pady=0, bd=8, fg="black", bg="powder blue", font=('arial', 20, 'bold'), text="=", command=BtnEquals).grid(row=4, column=2)
Division = Button(root, padx=16, pady=0, bd=8, fg="black", bg="powder blue", font=('arial', 20, 'bold'), text="/", command=lambda:BtnClick("/")).grid(row=4, column=3)
#=====================================================End Of Buttons============================================================================================
root.mainloop()
