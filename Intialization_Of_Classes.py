import os
import ReadFile as rf
import collections
from prettytable import PrettyTable

class Repository:
    ''' Store all info about students and instructors '''
    def __init__(self, info_dir, ptables = True):
        self.info_dir = info_dir # string - directory with students, instructors, grades files
        self._students = collections.defaultdict() # key: cwid, value: instances of Student
        self._instructors = collections.defaultdict() # key: cwid, value: instances of Instructor

        try:
            self._get_students(os.path.join(info_dir, 'students.txt'))
            self._get_instructors(os.path.join(info_dir, 'instructors.txt'))
            self._get_grades(os.path.join(info_dir, 'grades.txt'))
        except ValueError as ve:
            print(ve)
        except FileNotFoundError as fnfe:
            print(fnfe)

        if ptables:
            print("\nStudents Summary")
            self.student_table()
            print("\nInstructor Summary")
            self.instructor_table()
        
    def _get_students(self, path):
        ''' Read students from path and add to the self.students
            Allow exceptions from reading the file to flow back to the caller.
        '''
        for cwid, name, major in rf.file_reading_gen(path, 3, sep='\t', header=False):
            self._students[cwid] = Student(cwid, name, major)
    
    def _get_instructors(self, path):
        ''' Read instructors from path and add to the self.instructors
            Allow exceptions from reading the file to flow back to the caller.
        '''
        for cwid, name, dept in rf.file_reading_gen(path, 3, sep='\t', header=False):
            self._instructors[cwid] = Instructor(cwid, name, dept)

    def _get_grades(self, path):
        ''' Read grades from path and add to the self.instructors
            Allow exceptions from reading the file to flow back to the caller.
        '''
        for student_cwid, course, grade, instructor_cwid in rf.file_reading_gen(path, 4, sep='\t', header=False):
            if student_cwid in self._students:
                self._students[student_cwid].add_course(course, grade)
            else:
                print(f"Found grade for unknown student '{student_cwid}")
            if instructor_cwid in self._instructors:
                self._instructors[instructor_cwid].add_student(course)
            else:
                print(f"Found grade for unknown instructor '{instructor_cwid}")
    
    def student_table(self):
        ''' print a PrettyTable with a summary of all students '''
        pt = PrettyTable(field_names=Student.pt_hdr)
        for student in self._students.values():
            pt.add_row(student.pt_row())
        print(pt)

    def instructor_table(self):
        ''' print a PrettyTable with a summary of all instructors '''
        pt = PrettyTable(field_names=Instructor.pt_hdr)
        for instructor in self._instructors.values():
            #  each instructor may teach many classes
            for row in instructor.pt_row():
                pt.add_row(row)
        print(pt)


class Student:
    ''' Represent a single student '''
    pt_hdr = ['CWID', 'Name', 'Completed Courses']

    def __init__(self, cwid, name, major):
        self._cwid = cwid
        self._name = name
        self._major = major
        self._courses = collections.defaultdict(str) # key: courses, value: str - grade

    def add_course(self, course, grade):
        """ Note that the student took a course """
        self._courses[course] = grade

    def pt_row(self):
        """ return a list of values to populate the prettyTable for this student """
        return [self._cwid, self._name, sorted(self._courses.keys())]


class Instructor:
    ''' Represent a instructor '''
    pt_hdr = ['CWID', 'Name', 'Dept', 'Courses', 'Students']

    def __init__(self, cwid, name, dept):
        self._cwid = cwid
        self._name = name
        self._dept = dept
        self._courses = collections.defaultdict(int) # key: courses, value: number of students

    def add_student(self, course):
        """ Note that the another student took the course with this instructor """
        self._courses[course] += 1

    def pt_row(self):
        """ A generator returning rows to be added to the Instructor prettytable
            The prettytable includes only those instructors who have taught at least one course.
        """
        for course, count in self._courses.items():
            yield [self._cwid, self._name, self._dept, course, count]

def main():
    directory = '/Users/hangboli/Documents/GitHub/Student-Info-Management-System/'

    _ = Repository(directory)


if __name__ == '__main__':
    main()



