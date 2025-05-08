def add_course(record, course):
    updated_courses = tuple(record[2]) + (course,)
    return (record[0], record[1], updated_courses)