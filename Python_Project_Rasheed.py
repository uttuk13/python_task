import json
import sqlite3

#connecting database
conn = sqlite3.connect('librarydatabase.db')
print ("Opened database successfully")
#Creating Tables
conn.execute('''CREATE TABLE PAPERBOOKTABLE
            (
            Title           TEXT    NOT NULL,
            Author          TEXT     NOT NULL,
            Published_year        TEXT NOT NULL,
            ISBN TEXT NOT NULL,
            NOP TEXT NOT NULL         );''')
conn.execute('''CREATE TABLE EBOOKTABLE
            (
            Title           TEXT    NOT NULL,
            Author           TEXT     NOT NULL,
            Published_year        TEXT NOT NULL,
            FileType         TEXT NOT NULL);''')
class removingbookerror(Exception):
     def __str__(self):
        return f" book not found"
class Book:
    def __init__(self,title,author,publication_year):
        self.title=title
        self.author=author
        self.publication_year=publication_year
class EBook(Book):
   def __init__(self, title, author, publication_year, filetype):
       self.filetype=filetype
       super().__init__(title, author, publication_year)
class PaperBook(Book):
    def __init__(self, title, author, publication_year,ISBN,number_of_page):
        self.ISBN=ISBN
        self.number_of_page=number_of_page
        super().__init__(title, author, publication_year)
class Library():
    d={}
    def add_book(self,x):
        self.x=x
        if(type(self.x)==EBook):
            Library.d[self.x.title]=[self.x.author,self.x.publication_year,self.x.filetype]
            t=str(self.x.title)
            py=str(self.x.publication_year)
            at=str(self.x.author)
            ft=str(self.x.filetype)
            conn.execute(f"insert into EBOOKTABLE(Title, Author, Published_year, FileType) VALUES ('{t}','{at}','{py}','{ft}')")

        elif(type(self.x)==PaperBook):
            Library.d[self.x.title]=[self.x.author,self.x.publication_year,self.x.ISBN,self.x.number_of_page]
            t=str(self.x.title)
            py=str(self.x.publication_year)
            isbn=str(self.x.ISBN)
            nopg=str(self.x.number_of_page)
            at=str(self.x.author)
        #writing into the json file
        with open('data.json', 'w') as fp:
            json.dump(Library.d, fp)
    def display_books(self):
        #Reading from json file
        # with open('data.json') as json_file:
        #     data = json.load(json_file)
        cursor = conn.execute("SELECT Title from PAPERBOOKTABLE")
        print("Ebooks are")
        k=conn.execute("select Title from EBOOKTABLE")
        for i in k:
            print(i)
        for i in cursor:
            print(i)    
        
    def remove_book(self,title):
        self.title=title
        try:
            del Library.d[self.title]
        except:
            x=removingbookerror()
            print(x)


l=Library()


l.display_books()
a=int(input("1 for adding book \n 2 for removing book \n 3 for displaying all books"))
if(a==1):
    bn=input("Enter Book Name")
    ba=input("Enter Author name")
    by=input("Enter The Publishing Year")
    ty=input("Enter Doc type or page numbers")
    try:
        int(ty)
        p1=PaperBook(bn,ba,by,ty)
        l.add_book(p1)
    except:
        p1=EBook(bn,ba,by,ty)
        l.add_book(p1)
elif a==2:
    rm=input("Enter the book title")
    l.remove_book(rm)
elif a==3:
    l.display_books()
else:
    print("Please select proper option")



        