from werkzeug.security import generate_password_hash

letters = list("Major")
dir_name = ""
for letter in letters:
    dir_name += str(ord(letter))
print(dir_name)
print(generate_password_hash("12345"))