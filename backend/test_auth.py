from db_operations import sign_up, sign_in

email1 = "john_doe@example.com"
password1= "john_doe_1234"

email2 = "mikemao1027@gmail.com"
password2 = "Sqwible@31415"

ok, msg = sign_up("John", "Doe", "jd12", email1, password1, "123-456-7890", "Computer Science")
print("Sign Up: ", ok, msg)

ok, user_id = sign_in(email1, password1)
print("Sign In With Correct Password: ", ok, user_id)

ok, user_id = sign_in(email1, "jane_doe_1234")
print("Sign In With Wrong Password: ", ok, user_id)

ok, msg = sign_up("Mike", "Mao", "mm386", email2, password2, "425-625-1498", "Computer Science")
print("Sign Up, ", ok, msg)

ok, user_id = sign_in(email2, password2)
print("Sign In With Correct Password ", email2, user_id)