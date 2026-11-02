def getGrade(mark):
    if mark >= 90:
        return "A"
    elif mark >= 80:
        return "B"
    elif mark >= 70:
        return "C"
    elif mark >= 60:
        return "D"
    else:
        return "E"


def processStudentMarks(student_grades):
    print("\nStudent Details:")
    print("\nName\tMark\tGrade")
    if not student_grades:
        print("No student marks to process.")
        return

    for name, mark in student_grades:
        print(f"{name}\t\t{mark}\t{getGrade(int(mark))}")
    print("---+---+---+---+---")

    marks = [int(mark) for _, mark in student_grades]
    print(
        f"\nAverage: {sum(marks) / len(student_grades):.1f}\tHighest Mark: {max(marks)}\tLowest Mark: {min(marks)}"
    )


def getStudentMarks():
    student_grades = []
    while True:
        name = input("Enter the name of the student: ").strip()

        # Check for duplicate student names
        duplicate_name = False
        for student_name, _ in student_grades:
            if student_name.casefold() == name.casefold():
                print(
                    f"{name} has already been entered. Please enter a different student."
                )
                duplicate_name = True
                break

        if duplicate_name:
            continue

        mark = input(f"Enter the mark for {name}: ")

        # Validate the mark input
        if not mark.isdigit() or not (0 <= int(mark) <= 100):
            print("Please enter a valid mark between 0 and 100.")
            continue

        # Add the student name and mark to the list
        student_grades.append((name.title(), mark))
        continue_input = input("Do you want to enter another student's mark? (y/n): ")
        if continue_input.lower() != "y":
            show_results = input("Do you want to see the results now? (y/n): ")
            if show_results.lower() == "y":
                processStudentMarks(student_grades)
            break
    return student_grades


getStudentMarks()
