from class_items import Book

game = 1
a = [Book(game) for _ in range(5)]
for i in range(5):
    a[i].number = i
found_book = next((item for item in a if item.number == 6), None)
print(a)
print(found_book, found_book.number)