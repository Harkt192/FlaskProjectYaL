# dirname = input()
# letters = list(dirname)
# dir_name = ""
# for letter in letters:
#     dir_name += str(ord(letter)).ljust(5, "0")
# print(dir_name)

from werkzeug.security import generate_password_hash, check_password_hash

a = generate_password_hash("RASDWAEWQ231" * 3000)
b = "RASDWAEWQ231" * 3000
print(a, b, sep="\n")
print(a == b)
print(check_password_hash(a, b))