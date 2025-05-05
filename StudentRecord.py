def create_student_record():
    name = input("Enter student name: ")
    student_id = input("Enter student ID: ")
    courses_input = input("Enter courses/strand (separated by commas): ")
    courses = courses_input.split(",")
    return (name, student_id, courses)

record = create_student_record()
print("Student Record:", record)
#GROUP 6 ABG