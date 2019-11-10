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
        self._majors = collections.defaultdict() # key:cwid, value:instance of Major

        try:
            self._get_majors(os.path.join(info_dir, 'majors.txt'))
            self._get_students(os.path.join(info_dir, 'students.txt'))
            self._get_instructors(os.path.join(info_dir, 'instructors.txt'))
            self._get_grades(os.path.join(info_dir, 'grades.txt'))        
        except ValueError as ve:
            print(ve)
        except FileNotFoundError as fnfe:
            print(fnfe)

        if ptables:
            print("\nMajor Summary")
            self.majors_table()
            print("\nStudents Summary")
            self.student_table()
            print("\nInstructor Summary")
            self.instructor_table()
        
    def _get_majors(self, path):
        """ Read majors files and assign the course to the majors 
            Handle exceptions in the calling function.
        """
        for major, flag, course in rf.file_reading_gen(path, 3, sep='\t', header=True):
            if major not in self._majors:
                self._majors[major] = Major(major)
            self._majors[major].add_course(course, flag)

    def _get_students(self, path):
        ''' Read students from path and add to the self.students
            Allow exceptions from reading the file to flow back to the caller.
        '''
        for cwid, name, major in rf.file_reading_gen(path, 3, sep=';', header=True):
            if major not in self._majors:
                print(f"Student {cwid} '{name}' has unknown major '{major}'")
            else:
                self._students[cwid] = Student(cwid, name, self._majors[major])
    
    def _get_instructors(self, path):
        ''' Read instructors from path and add to the self.instructors
            Allow exceptions from reading the file to flow back to the caller.
        '''
        for cwid, name, dept in rf.file_reading_gen(path, 3, sep='|', header=True):
            self._instructors[cwid] = Instructor(cwid, name, dept)

    def _get_grades(self, path):
        ''' Read grades from path and add to the self.instructors
            Allow exceptions from reading the file to flow back to the caller.
        '''
        for student_cwid, course, grade, instructor_cwid in rf.file_reading_gen(path, 4, sep='|', header=True):
            if student_cwid in self._students:
                self._students[student_cwid].add_course(course, grade)
            else:
                print(f"Found grade for unknown student '{student_cwid}")
            if instructor_cwid in self._instructors:
                self._instructors[instructor_cwid].add_student(course)
            else:
                print(f"Found grade for unknown instructor '{instructor_cwid}")
    
    def majors_table(self):
        ''' print a PrettyTable with a summary of all majors '''
        pt = PrettyTable(field_names=Major.PT_HDR)
        for major in self._majors.values():
            pt.add_row(major.pt_row())
        print(pt)
    

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
    pt_hdr = ['CWID', 'Name', 'Major', 'Completed Courses', 'Remaining Required', 'Remaining Electives']

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
        major, passed, rem_required, rem_electives = self._major.remaining(self._courses)
        return [self._cwid, self._name, major, sorted(passed), rem_required, rem_electives]


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

class Major:
    """ Track the required courses and electives for each major.
        Provide a mechanism to store new courses and electives.
        Provide a mechanism to identify the remaining required and elective courses given a set of passed course.
    """
    PT_HDR = ['Major', 'Required Courses', 'Electives']
    PASSING_GRADES = {'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C'}
    
    def __init__(self, dept):
        self._dept = dept
        self._required = set() #set of required courses for the major - All must be taken
        self._electives = set() #set of electives - only one must be taken
    
    def add_course(self, course, type):
        """ add a new course to the major where type is either
            'R' for required or 'E' for elective
        """
        if type == 'R':
            self._required.add(course)
        elif type == 'E':
            self._electives.add(course)
        else:
            raise ValueError(f"Major.add_course: expected 'R' or 'E' but found '{type}' ")
    
    def remaining(self, completed):
        """ Given a list of completed courses, calculate the reamaining required and electived courses.
            Completed is a dict where the key is the courses completed and the grades are in PASSING_GRADES.
            Return a tuple of (passed, rem_required, rem_electives)
        """
        passed = {course for course, grade in completed.items() if grade in Major.PASSING_GRADES}
        rem_required = self._required - passed

        if self._electives.intersection(passed):
            rem_electives = None
        else:
            rem_electives = self._electives
        return self._dept, passed, rem_required, rem_electives
    
    def pt_row(self):
        """ Return a list of values to include in the Majors prettytable """
        return [self._dept, sorted(self._required), sorted(self._electives)]


def main():
    directory = '/Users/hangboli/Documents/GitHub/Student-Info-Management-System/'

    _ = Repository(directory)


if __name__ == '__main__':
    main()



