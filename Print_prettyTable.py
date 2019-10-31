import Initialization_Class_Student_Instructor
from prettytable import PrettyTable


def print_table():
    students, instructors, course_students_instructors, courses = Initialization_Class_Student_Instructor.all_list()

    pt1 = PrettyTable(field_names=["CWID", "Name", "Completed Courses"])
    pt2 = PrettyTable(field_names=["CWID", "Name", "Dept", "Courses", "Students"])
    example = []

    for course in courses:
        """Add data from dictionary files_summary"""
        temp =[]
        for instructor in instructors:
            if courses[course][0][2] == instructor.CWID:

                temp.extend([instructor.CWID, instructor.Name, instructor.Department, course, len(courses[course])])

        example.append(temp)

    example = sorted(example, key=lambda x: x[0])
    for i in example:
        pt2.add_row(i)


    for student in students:
        for course in courses:
            for item in courses[course]:
                if item[0] == student.CWID:
                    student.course_rank[course] = item[1]

    for s in students:
        example2 = '['
        for course in s.course_rank:
            example2 += course + ', '
        example2 = example2[:-2]
        example2 += ']'

        pt1.add_row([s.CWID, s.Name, example2])

    print(pt1)
    print(pt2)

if __name__ == '__main__':
    # print("SSS")
    print_table()