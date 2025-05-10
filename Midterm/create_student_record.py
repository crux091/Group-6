def create_student_record():
    #Rick Francis Cruz
    name = input("\nEnter student name: ")
    student_id = input("Enter student ID: ")

    courses = []  # Initialize an empty list for courses
    print("Enter your courses one by one. Type 'done' when finished:")
    
    while True:
        course = input("Enter course name: ")
        if course.lower() == "done":
            break
        courses.append(course)

    return (name, student_id, tuple(courses))