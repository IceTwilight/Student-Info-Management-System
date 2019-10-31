import collections
import ReadFile as rf
import os


class Student:
    def __init__(self, CWID, Name, Major):
        self.CWID, self.Name, self.Major = CWID, Name, Major
        self.course_rank = collections.defaultdict(str)


class Instructor:
    def __init__(self, CWID, Name, Department):
        self.CWID, self.Name, self.Department = CWID, Name, Department
        self.course_students = collections.defaultdict(int)


def create_list(table_type: str, columns: int, header: bool, result: list, typeClass):
    path_cur_directory = os.getcwd()
    path = path_cur_directory + '/' + table_type + '.txt'
    for item in rf.file_reading_gen(path, columns, header=header):
        result.append(typeClass(item[0], item[1], item[2]))


def create_grade_list(result):
    path_cur_directory = os.getcwd()
    path = path_cur_directory + '/grades.txt'
    for item in rf.file_reading_gen(path, 4, header=False):
        result.append([item[0], item[1], item[2], item[3]])
    course = collections.defaultdict(list)
    for item in result:
        course[item[1]].append([item[0], item[2], item[3]])
    return course


def all_list():
    students, instructors, course_students_instructors, courses = [], [], [], collections.defaultdict(list)
    create_list('students', 3, False, students, Student)
    create_list('instructors', 3, False, instructors, Instructor)
    courses = create_grade_list(course_students_instructors)
    return students, instructors, course_students_instructors, courses


if __name__ == '__main__':
    # print("SSS")
    all_list()
