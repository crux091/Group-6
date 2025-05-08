from create_student_record import create_student_record
from get_name import get_name
from get_student_id import get_student_id
from get_courses import get_courses
from add_course import add_course 

num_students = int(input("How many student records you want to create? "))
student_records = [create_student_record() for _ in range(num_students)] # line 7 and 8 - Raiza

print("\nStudent Records:")
for i, record in enumerate(student_records, start=1):  # Start indexing from 1
    print(f"{i}: Name: {get_name(record)}, ID: {get_student_id(record)}, Courses: {get_courses(record)}") # Line 10 to 12 - Nairb

add_more = input("\nDo you want to add a course to a student record? (yes/no): ").lower()
if add_more == "yes":
    student_index = int(input(f"Enter record number (1-{num_students}): ")) - 1  # Adjust index to match list position
    student_records[student_index] = add_course([student_records[student_index]])[0]

    print("\nUpdated Record:")
    print(f"Name: {get_name(student_records[student_index])}, ID: {get_student_id(student_records[student_index])}, Courses: {get_courses(student_records[student_index])}")
    # Line 14 to 20 - Nairb and Rick    